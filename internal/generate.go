package internal

import (
	"fmt"
	"log"
	"os"
	"os/user"
	"path/filepath"

	"bchmnn/poodle-cli/internal/util"

	"github.com/mvdan/sh/shell"
)

type Generator struct {
	GeneratorName      string
	Input              string
	OutPath            string
	TemplateDir        string
	IgnoreFileOverride string
	GeneratorArgs      []string
	ImageVersion       string
	UseDocker          bool
	Log                *log.Logger
}

func NewGenerator(generatorName string, input string, outPath string, templateDir string, ignoreFileOverride string, generatorArgs []string, imageVerison string, useDocker bool) *Generator {
	return &Generator{
		GeneratorName:      generatorName,
		Input:              input,
		OutPath:            outPath,
		TemplateDir:        templateDir,
		IgnoreFileOverride: ignoreFileOverride,
		GeneratorArgs:      generatorArgs,
		ImageVersion:       imageVerison,
		UseDocker:          useDocker,
		Log:                log.New(os.Stdout, "[GENERATOR] ", log.LstdFlags),
	}
}

func (g *Generator) Generate() error {
	err := util.MakeDirIfNotExists(g.OutPath, false)
	if err != nil {
		return err
	}
	if g.IgnoreFileOverride != "" {
		util.Copy(g.IgnoreFileOverride, g.OutPath+"/.openapi-generator-ignore")
	}
	if g.UseDocker {
		err = g.ProcessDocker()
	} else {
		err = g.ProcessNative()
	}
	return err
}

func (g *Generator) ProcessDocker() error {
	absInputPath, err := filepath.Abs(g.Input)
	if err != nil {
		return err
	}

	inputName := filepath.Base(absInputPath)

	absOutPath, err := filepath.Abs(g.OutPath)
	if err != nil {
		return err
	}

	user, err := user.Current()
	if err != nil {
		return err
	}

	args := []string{
		"run",
		"--rm",
		"-v",
		fmt.Sprintf("%s:/input_%s", absInputPath, inputName),
		"-v",
		fmt.Sprintf("%s:/out", absOutPath),
	}

	if g.TemplateDir != "" {
		absTemplatePath, err := filepath.Abs(g.TemplateDir)
		if err != nil {
			return err
		}
		args = append(args,
			"-v",
			fmt.Sprintf("%s:/template", absTemplatePath),
		)
	}

	args = append(args,
		"-u",
		fmt.Sprintf("%s:%s", user.Uid, user.Gid),
		fmt.Sprintf("openapitools/openapi-generator-cli:%s", g.ImageVersion),
		"generate",
		"-g",
		g.GeneratorName,
	)

	if g.TemplateDir != "" {
		args = append(args,
			"-t",
			"/template",
		)
	}

	args = append(args,
		"-i",
		fmt.Sprintf("/input_%s", inputName),
		"-o",
		"/out",
	)

	for _, argsString := range g.GeneratorArgs {
		additionalArgs, err := shell.Fields(argsString, nil)
		if err != nil {
			return err
		}
		args = append(args, additionalArgs...)
	}

	process := util.Process{
		Name: "docker",
		Arg:  args,
		Stdout: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI-DOCKER] ",
			Writer: os.Stdout,
		},
		Stderr: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI-DOCKER] ",
			Writer: os.Stderr,
		},
	}

	g.Log.Println("Running:", process.String())

	return process.Run()
}

func (g *Generator) ProcessNative() error {
	args := []string{
		"generate",
		"-g",
		g.GeneratorName,
	}

	if g.TemplateDir != "" {
		args = append(args,
			"-t",
			g.TemplateDir,
		)
	}

	args = append(args,
		"-i",
		g.Input,
		"-o",
		g.OutPath,
	)

	for _, argsString := range g.GeneratorArgs {
		additionalArgs, err := shell.Fields(argsString, nil)
		if err != nil {
			return err
		}
		args = append(args, additionalArgs...)
	}

	process := util.Process{
		Name: "openapi-generator-cli",
		Arg:  args,
		Stdout: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI] ",
			Writer: os.Stdout,
		},
		Stderr: &util.ProcessWriter{
			Prefix: "[OPENAPI-GEN-CLI] ",
			Writer: os.Stderr,
		},
	}

	g.Log.Println("Running:", process.String())

	return process.Run()
}
