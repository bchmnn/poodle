package cmd

import (
	"fmt"
	"os"
	"strings"

	"bchmnn/poodle-cli/internal"
	"bchmnn/poodle-cli/internal/util"

	"github.com/spf13/cobra"
)

func NewExtractCommand() *cobra.Command {
	var (
		moodlePath       string
		moodleDockerPath string
		outPath          string
		parents          bool
	)

	var cmd = &cobra.Command{
		Use:     "extract [flags] <moodle-directory>",
		Short:   "Extract moodle webservice methods with their request and response types",
		Example: "  poodle extract -d ./moodle-docker -o webservices@{VERSION}.json ./moodle",
		Args:    cobra.MatchAll(cobra.ExactArgs(1), cobra.OnlyValidArgs),
		RunE: func(cmd *cobra.Command, args []string) error {
			moodlePath = args[0]
			err := util.IsValidDir(moodlePath)
			if err != nil {
				return err
			}
			if moodleDockerPath != "" {
				err = util.IsValidDir(moodleDockerPath)
				if err != nil {
					return err
				}
			}
			moodle, err := util.NewMoodle(moodlePath)
			if err != nil {
				return err
			}
			var toStdout = true
			if outPath != "" {
				toStdout = false
				if strings.Contains(outPath, "{VERSION}") {
					outPath = strings.ReplaceAll(outPath, "{VERSION}", moodle.GetVersionString())
				}
				if strings.Contains(outPath, "{COMMIT}") {
					commit, err := moodle.GetGitCommit()
					if err != nil {
						return err
					}
					outPath = strings.ReplaceAll(outPath, "{COMMIT}", commit)
				}
				if strings.Contains(outPath, "{TAG}") {
					tag, err := moodle.GetGitTag()
					if err != nil {
						return err
					}
					outPath = strings.ReplaceAll(outPath, "{TAG}", tag)
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
			}

			extractor := internal.NewExtractor(moodle, moodleDockerPath, outPath, toStdout)
			err = extractor.Extract()
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %s", err)
				os.Exit(1)
			}
			return nil
		},
	}

	cmd.Flags().StringVarP(&moodleDockerPath, "docker", "d", "", "path to moodlehq/moodle-docker")
	cmd.Flags().StringVarP(&outPath, "outpath", "o", "", "path to output file. Possible substitutes: {VERSION}, {COMMIT}, {TAG}")
	cmd.Flags().BoolVar(&parents, "parents", false, "make parent directories of path given with --outpath")

	return cmd
}
