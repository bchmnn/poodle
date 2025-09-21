package internal

import (
	"fmt"
	"log"
	"os"
	"os/user"
	"path/filepath"

	"bchmnn/poodle-cli/internal/util"
)

type Templator struct {
	Name         string
	Patches      []string
	OutPath      string
	ImageVersion string
	UseDocker    bool
	Log          *log.Logger
}

func NewTemplator(name string, patches []string, outPath string, imageVersion string, useDocker bool) *Templator {
	return &Templator{
		Name:         name,
		Patches:      patches,
		OutPath:      outPath,
		ImageVersion: imageVersion,
		UseDocker:    useDocker,
		Log:          log.New(os.Stdout, "[TEMPLATOR] ", log.LstdFlags),
	}
}

func (t *Templator) Process() error {
	var err error
	if t.UseDocker {
		err = t.ProcessDocker()
	} else {
		err = t.ProcessNative()
	}
	if err != nil {
		return err
	}

	return t.Patch()
}

func (t *Templator) ProcessDocker() error {
	err := util.MakeDirIfNotExists(t.OutPath, false)
	if err != nil {
		return err
	}

	absPath, err := filepath.Abs(t.OutPath)
	if err != nil {
		return err
	}

	user, err := user.Current()
	if err != nil {
		return err
	}

	process := util.Process{
		Name: "docker",
		Arg: []string{
			"run",
			"--rm",
			"-v",
			fmt.Sprintf("%s:/out", absPath),
			"-u",
			fmt.Sprintf("%s:%s", user.Uid, user.Gid),
			fmt.Sprintf("openapitools/openapi-generator-cli:%s", t.ImageVersion),
			"author",
			"template",
			"-g",
			t.Name,
			"-o",
			"/out",
		},
		Stdout: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI-DOCKER] ",
			Writer: os.Stdout,
		},
		Stderr: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI-DOCKER] ",
			Writer: os.Stderr,
		},
	}

	t.Log.Println("Running:", process.String())

	return process.Run()
}

func (t *Templator) ProcessNative() error {
	process := util.Process{
		Name: "openapi-generator-cli",
		Arg: []string{
			"author",
			"template",
			"-g",
			t.Name,
			"-o",
			t.OutPath,
		},
		Stdout: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI] ",
			Writer: os.Stdout,
		},
		Stderr: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI] ",
			Writer: os.Stderr,
		},
	}

	t.Log.Println("Running:", process.String())

	return process.Run()
}

func (t *Templator) Patch() error {
	for _, patch := range t.Patches {
		absPath, err := filepath.Abs(patch)
		if err != nil {
			return err
		}

		process := util.Process{
			Name: "patch",
			Arg: []string{
				"-p1",
				"-d",
				t.OutPath,
				"-i",
				absPath,
			},
			Stdout: &util.ProcessWriter{
				Prefix: "[PATCH] ",
				Writer: os.Stdout,
			},
			Stderr: &util.ProcessWriter{
				Prefix: "[PATCH] ",
				Writer: os.Stderr,
			},
		}

		t.Log.Println("Running:", process.String())

		err = process.Run()
		if err != nil {
			return err
		}
	}
	return nil
}
