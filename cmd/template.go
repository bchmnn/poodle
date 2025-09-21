package cmd

import (
	"fmt"
	"os"

	"bchmnn/poodle-cli/internal"
	"bchmnn/poodle-cli/internal/util"

	"github.com/spf13/cobra"
)

func NewTemplateCommand() *cobra.Command {
	var (
		template     string
		patches      []string
		outPath      string
		parents      bool
		imageVersion string
		useDocker    bool
	)

	var cmd = &cobra.Command{
		Use:     "template <name>",
		Short:   "Export openapitools/openapi-generator-cli template",
		Example: "  poodle template python -o python-template -p patches/python/1.patch",
		Args:    cobra.MatchAll(cobra.ExactArgs(1), cobra.OnlyValidArgs),
		RunE: func(cmd *cobra.Command, args []string) error {
			var err error
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

			template = args[0]
			for _, patch := range patches {
				err := util.IsValidFile(patch)
				if err != nil {
					return err
				}
			}
			templator := internal.NewTemplator(template, patches, outPath, imageVersion, useDocker)
			err = templator.Process()
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %s", err)
				os.Exit(1)
			}
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&patches, "patch", "p", nil, "patches to apply to template (multiple occurrences possible)")
	cmd.Flags().StringVarP(&outPath, "outpath", "o", "", "path where to export template to")
	cmd.Flags().BoolVar(&parents, "parents", false, "make parent directories of path given with --outpath")
	cmd.Flags().StringVarP(&imageVersion, "image-version", "i", "latest", "docker image version of openapitools/openapi-generator-cli to use if --use-docker flag is set")
	cmd.Flags().BoolVarP(&useDocker, "use-docker", "d", false, "use openapitools/openapi-generator-cli image instead of native installation")

	return cmd
}
