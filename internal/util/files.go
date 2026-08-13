package util

import (
	"fmt"
	"io"
	"net"
	"os"
	"path/filepath"
	"strings"

	cp "github.com/otiai10/copy"
)

func GetFreePort() (int, error) {
	// https://github.com/phayes/freeport
	//
	// Open Source License (BSD 3-Clause)
	//
	// Copyright (c) 2014, Patrick Hayes / HighWire Press All rights reserved.
	//
	// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
	//
	//     Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
	//
	//     Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
	//
	//     Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
	//
	// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	addr, err := net.ResolveTCPAddr("tcp", "localhost:0")
	if err != nil {
		return 0, err
	}

	l, err := net.ListenTCP("tcp", addr)
	if err != nil {
		return 0, err
	}
	defer l.Close()
	return l.Addr().(*net.TCPAddr).Port, nil
}

func NodeInValidDir(path string) error {
	parentDir := filepath.Dir(path)
	return IsValidDir(parentDir)
}

func IsValidFile(path string) error {
	info, err := os.Stat(path)
	if os.IsNotExist(err) {
		return fmt.Errorf("%s does not exist", path)
	}
	if err != nil {
		return err
	}
	if info.IsDir() {
		return fmt.Errorf("%s is a directory", path)
	}
	return nil
}

func IsValidDir(path string) error {
	info, err := os.Stat(path)
	if os.IsNotExist(err) {
		return fmt.Errorf("%s does not exist", path)
	}
	if err != nil {
		return err
	}
	if !info.IsDir() {
		return fmt.Errorf("%s is not a directory", path)
	}
	return nil
}

func MakeDirIfNotExists(path string, onlyParent bool) error {
	if onlyParent {
		path = filepath.Dir(path)
	}
	stat, err := os.Stat(path)
	if os.IsNotExist(err) {
		return os.Mkdir(path, os.ModePerm)
	}
	if err != nil {
		return err
	}
	if stat.IsDir() {
		return nil
	} else {
		return fmt.Errorf("%s is a file", path)
	}
}

func MakeDirAllIfNotExists(path string, onlyParent bool) error {
	if onlyParent {
		path = filepath.Dir(path)
	}
	stat, err := os.Stat(path)
	if os.IsNotExist(err) {
		return os.MkdirAll(path, os.ModePerm)
	}
	if err != nil {
		return err
	}
	if stat.IsDir() {
		return nil
	} else {
		return fmt.Errorf("%s is a file", path)
	}
}

func Copy(src string, target string) error {
	return cp.Copy(src, target, cp.Options{
		OnSymlink: func(string) cp.SymlinkAction { return cp.Skip },
	})
}

func FileGetLines(path string) ([]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	data, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	return lines, nil
}
