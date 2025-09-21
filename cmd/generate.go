package cmd

import (
	"fmt"
	"os"

	"bchmnn/poodle-cli/internal"
	"bchmnn/poodle-cli/internal/util"

	"github.com/spf13/cobra"
)

func NewGenerateCommand() *cobra.Command {
	var (
		generatorName      string
		input              string
		outPath            string
		parents            bool
		templateDir        string
		ignoreFileOverride string
		generatorArgs      []string
		imageVersion       string
		useDocker          bool
	)

	var cmd = &cobra.Command{
		Use:     "generate <name> [flags] <input>",
		Short:   "Generate api client",
		Example: "  poodle generate python --parents -do gen/python -t templates/python spec@v5.0.2.json",
		Args:    cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs),
		RunE: func(cmd *cobra.Command, args []string) error {
			generatorName = args[0]
			input = args[1]
			err := util.IsValidFile(input)
			if err != nil {
				return err
			}
			if templateDir != "" {
				err := util.IsValidDir(templateDir)
				if err != nil {
					return err
				}
			}
			if ignoreFileOverride != "" {
				err := util.IsValidFile(ignoreFileOverride)
				if err != nil {
					return err
				}
			}
			if parents {
				err = util.MakeDirAllIfNotExists(outPath, true)
				if err != nil {
					return err
				}
			} else {
				err = util.NodeInValidDir(outPath)
				if err != nil {
					return err
				}
			}

			generator := internal.NewGenerator(generatorName, input, outPath, templateDir, ignoreFileOverride, generatorArgs, imageVersion, useDocker)
			err = generator.Generate()
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %s", err)
				os.Exit(1)
			}
			return nil
		},
	}

	cmd.Flags().StringVarP(&outPath, "outpath", "o", "", "path where to export template to")
	cmd.Flags().BoolVar(&parents, "parents", false, "make parent directories of path given with --outpath")
	cmd.Flags().StringVarP(&templateDir, "template", "t", "", "path to custom template")
	cmd.Flags().StringVar(&ignoreFileOverride, "ignore-file-override", "", "path to .openapi-generator-ignore")
	cmd.Flags().StringSliceVarP(&generatorArgs, "generator-args", "a", nil, "arguments that are forwarded to openapi-generator-cli (multiple occurrences possible, format \"--arg1 --arg2\" possible)")
	cmd.Flags().StringVarP(&imageVersion, "image-version", "i", "latest", "docker image version of openapitools/openapi-generator-cli to use if --use-docker flag is set")
	cmd.Flags().BoolVarP(&useDocker, "use-docker", "d", false, "use openapitools/openapi-generator-cli image instead of native installation")

	return cmd
}
