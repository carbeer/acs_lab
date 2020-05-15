package main

import "log"
import "bufio"
import "os"

func main() {
    fname := os.Args[1]
    
    f, err := os.Open(fname)
    if err != nil {
        log.Fatal(err)
    }

    defer func() {
        if err = f.Close(); err != nil {
            log.Fatal(err)
        }
    }()

    s := bufio.NewScanner(f)
    s.Scan()
    log.Println(s.Text())
}
