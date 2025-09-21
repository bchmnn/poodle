package util

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	cp "github.com/otiai10/copy"
)

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
