package util

import (
	"bytes"
	"fmt"
	"io"
	"os/exec"
	"strings"
)

type EnvItem struct {
	Key   string
	Value string
}

type ProcessWriter struct {
	Prefix string
	Writer io.Writer
	Buf    bytes.Buffer
}

func (p *ProcessWriter) Write(data []byte) (int, error) {
	total := len(data)
	for len(data) > 0 {
		i := bytes.IndexByte(data, '\n')
		if i < 0 {
			p.Buf.Write(data)
			break
		}
		p.Buf.Write(data[:i])
		line := p.Buf.String()
		p.Buf.Reset()

		if _, err := fmt.Fprintf(p.Writer, "%s%s\n", p.Prefix, line); err != nil {
			return 0, err
		}
		data = data[i+1:]
	}
	return total, nil
}

type Process struct {
	Name   string
	Arg    []string
	Env    []EnvItem
	Stdin  io.Reader
	Stdout io.Writer
	Stderr io.Writer
}

func (p *Process) setupCmd() *exec.Cmd {
	arg := p.Arg
	if arg == nil {
		arg = []string{}
	}
	cmd := exec.Command(p.Name, p.Arg...)
	if p.Env != nil {
		for _, envItem := range p.Env {
			entry := fmt.Sprintf("%s=%s", envItem.Key, envItem.Value)
			cmd.Env = append(cmd.Env, entry)
		}
	}
	return cmd
}

func (p *Process) HandleError(err error) error {
	if exitError, ok := err.(*exec.ExitError); ok {
		return fmt.Errorf("\"%s %s\" exited with exit code %d\n", p.Name, strings.Join(p.Arg, " "), exitError.ExitCode())
	} else {
		return exitError
	}
}

func (p *Process) Run() error {
	cmd := p.setupCmd()

	cmd.Stdout = p.Stdout
	cmd.Stderr = p.Stderr
	cmd.Stdin = p.Stdin

	if err := cmd.Run(); err != nil {
		return p.HandleError(err)
	}
	return nil
}

func (p *Process) Output() ([]byte, error) {
	cmd := p.setupCmd()
	cmd.Stderr = p.Stderr
	cmd.Stdin = p.Stdin

	output, err := cmd.Output()
	if err != nil {
		return nil, p.HandleError(err)
	}
	return output, nil
}

func (p *Process) String() string {
	b := new(strings.Builder)
	for _, e := range p.Env {
		b.WriteString(e.Key)
		b.WriteByte('=')
		b.WriteString(e.Value)
		b.WriteByte(' ')
	}
	b.WriteString(p.Name)
	for _, a := range p.Arg {
		b.WriteByte(' ')
		b.WriteString(a)
	}
	return b.String()
}

func HasExec(executable string) bool {
	_, err := exec.LookPath(executable)
	return err == nil
}
