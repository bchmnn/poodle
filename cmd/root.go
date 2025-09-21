package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use: "poodle",
}

func init() {
	rootCmd.AddCommand(NewExtractCommand())
	rootCmd.AddCommand(NewTemplateCommand())
	rootCmd.AddCommand(NewConvertCommand())
	rootCmd.AddCommand(NewGenerateCommand())
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}
