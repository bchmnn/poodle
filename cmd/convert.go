package cmd

import (
	"fmt"
	"os"
	"strings"

	"bchmnn/poodle-cli/internal"
	"bchmnn/poodle-cli/internal/util"

	"github.com/spf13/cobra"
)

func NewConvertCommand() *cobra.Command {
	var (
		input                 string
		outPath               string
		parents               bool
		moodlePath            string
		whitelistPath         string
		blacklistPath         string
		skipAddLoginTokenPath bool
		skipFixActivityBadge  bool
		skipFixDefaults       bool
		skipAddTags           bool
		skipPrettier          bool
	)

	var cmd = &cobra.Command{
		Use:     "convert [flags] <input>",
		Short:   "Convert moodle webservice methods to an OpenAPI Specification - Version 3.1",
		Example: "  poodle convert -m ./moodle -o openapi-spec@{VERSION}.json webservices@v5.0.2.json",
		Args:    cobra.MatchAll(cobra.ExactArgs(1), cobra.OnlyValidArgs),
		RunE: func(cmd *cobra.Command, args []string) error {
			input = args[0]
			err := util.IsValidFile(input)
			if err != nil {
				return err
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
			if blacklistPath != "" {
				err := util.IsValidFile(blacklistPath)
				if err != nil {
					return err
				}
			}
			if whitelistPath != "" {
				err := util.IsValidFile(whitelistPath)
				if err != nil {
					return err
				}
			}

			converter := internal.NewConverter(moodle, input, outPath, blacklistPath, whitelistPath, !skipAddLoginTokenPath, !skipFixActivityBadge, !skipFixDefaults, !skipAddTags, !skipPrettier, toStdout)
			err = converter.Convert()
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %s", err)
				os.Exit(1)
			}
			return nil
		},
	}

	cmd.Flags().StringVarP(&moodlePath, "moodle", "m", "", "path to moodle")
	cmd.Flags().StringVarP(&outPath, "outpath", "o", "", "path where to save openapi spec to")
	cmd.Flags().StringVar(&blacklistPath, "blacklist", "", "path to file containing disallowed methods")
	cmd.Flags().StringVar(&whitelistPath, "whitelist", "", "path to file containing allowed methods")
	cmd.Flags().BoolVar(&skipAddLoginTokenPath, "skip-add-login-token-path", false, "do not add path /login/token.php")
	cmd.Flags().BoolVar(&skipFixActivityBadge, "skip-fix-activity-badge", false, "don't set core_course_get_contents::modules::activitybadge to be a list or an object rather than only an object")
	cmd.Flags().BoolVar(&skipFixDefaults, "skip-fix-defaults", false, "don't fix default values to match types")
	cmd.Flags().BoolVar(&skipAddTags, "skip-add-tags", false, "do not set operation::tags to method::component (tags might result in multiple client classes)")
	cmd.Flags().BoolVar(&skipPrettier, "skip-prettier", false, "don't format result with prettier")
	cmd.Flags().BoolVar(&parents, "parents", false, "make parent directories of path given with --outpath")

	cmd.MarkFlagRequired("moodle")
	cmd.MarkFlagsMutuallyExclusive("blacklist", "whitelist")

	return cmd
}
