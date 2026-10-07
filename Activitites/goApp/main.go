package main

import (
	"fmt"
	"math/bits"
	"net"
	"os"
	"sort"
	"strconv"
)

type Subnet struct {
	Name   string
	Need   int
	Net    uint32
	Prefix int
}

func ipToU32(ip net.IP) uint32 {
	ip = ip.To4()
	return uint32(ip[0])<<24 | uint32(ip[1])<<16 | uint32(ip[2])<<8 | uint32(ip[3])
}

func u32ToIP(n uint32) net.IP {
	return net.IPv4(byte(n>>24), byte(n>>16), byte(n>>8), byte(n))
}

func mask(prefix int) uint32 {
	if prefix == 0 {
		return 0
	}
	return ^uint32(0) << (32 - prefix)
}

func flsm(base uint32, prefix, n int) ([]Subnet, error) {
	b := bits.Len(uint(n - 1)) // ceil(log2(n))
	newPrefix := prefix + b
	if newPrefix > 30 {
		return nil, fmt.Errorf("no hay bits suficientes: quedaría un /%d", newPrefix)
	}
	size := uint32(1) << (32 - newPrefix)
	total := 1 << b
	subs := make([]Subnet, 0, total)
	for i := 0; i < total; i++ {
		subs = append(subs, Subnet{
			Name:   fmt.Sprintf("Subred %d", i+1),
			Net:    base + uint32(i)*size,
			Prefix: newPrefix,
		})
	}
	return subs, nil
}

func vlsm(base uint32, prefix int, reqs []int) ([]Subnet, error) {
	sorted := append([]int(nil), reqs...)
	sort.Sort(sort.Reverse(sort.IntSlice(sorted)))

	end := uint64(base) + (uint64(1) << (32 - prefix))
	cur := uint64(base)
	subs := make([]Subnet, 0, len(sorted))

	for i, need := range sorted {
		h := bits.Len(uint(need + 1)) // 2^h >= need+2
		size := uint64(1) << h
		if cur+size > end {
			return nil, fmt.Errorf("no cabe la subred de %d hosts (faltan direcciones)", need)
		}
		subs = append(subs, Subnet{
			Name:   fmt.Sprintf("Subred %d", i+1),
			Need:   need,
			Net:    uint32(cur),
			Prefix: 32 - h,
		})
		cur += size
	}
	return subs, nil
}

func printTable(subs []Subnet) {
	fmt.Printf("%-10s %-8s %-8s %-18s %-16s %-16s %-16s %-16s\n",
		"Nombre", "Pedidos", "Útiles", "Red", "Máscara", "Primer host", "Último host", "Broadcast")
	for _, s := range subs {
		m := mask(s.Prefix)
		bc := s.Net | ^m
		usable := (1 << (32 - s.Prefix)) - 2
		fmt.Printf("%-10s %-8d %-8d %-18s %-16s %-16s %-16s %-16s\n",
			s.Name, s.Need, usable,
			fmt.Sprintf("%s/%d", u32ToIP(s.Net), s.Prefix),
			u32ToIP(m), u32ToIP(s.Net+1), u32ToIP(bc-1), u32ToIP(bc))
	}
}

func usage() {
	fmt.Println("Uso:")
	fmt.Println("  subnet flsm <red/prefijo> <num_subredes>")
	fmt.Println("  subnet vlsm <red/prefijo> <hosts1> <hosts2> ...")
	fmt.Println("Ej: subnet vlsm 192.168.10.0/24 100 50 25 10")
}

func main() {
	if len(os.Args) < 4 {
		usage()
		os.Exit(1)
	}
	_, ipnet, err := net.ParseCIDR(os.Args[2])
	if err != nil || ipnet.IP.To4() == nil {
		fmt.Fprintln(os.Stderr, "Red inválida (solo IPv4 en formato CIDR)")
		os.Exit(1)
	}
	prefix, _ := ipnet.Mask.Size()
	base := ipToU32(ipnet.IP)

	var subs []Subnet
	switch os.Args[1] {
	case "flsm":
		n, err := strconv.Atoi(os.Args[3])
		if err != nil || n < 1 {
			fmt.Fprintln(os.Stderr, "num_subredes inválido")
			os.Exit(1)
		}
		subs, err = flsm(base, prefix, n)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	case "vlsm":
		var reqs []int
		for _, a := range os.Args[3:] {
			v, err := strconv.Atoi(a)
			if err != nil || v < 1 {
				fmt.Fprintln(os.Stderr, "hosts inválido:", a)
				os.Exit(1)
			}
			reqs = append(reqs, v)
		}
		subs, err = vlsm(base, prefix, reqs)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	default:
		usage()
		os.Exit(1)
	}
	printTable(subs)
}
