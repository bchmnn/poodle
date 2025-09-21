package util

import (
	"errors"
	"fmt"
	"os"
	"regexp"
	"strconv"

	"github.com/go-git/go-git/v6"
	"github.com/go-git/go-git/v6/plumbing"
	"github.com/go-git/go-git/v6/plumbing/object"
)

type Moodle struct {
	Path     string
	Release  string
	Branch   string
	Maturity string
	Version  float64
}

func NewMoodle(path string) (*Moodle, error) {
	content, err := os.ReadFile(path + "/version.php")
	if err != nil {
		return nil, err
	}

	versionRegex := regexp.MustCompile(`\$version\s*=\s*([\d\.]+);`)
	releaseRegex := regexp.MustCompile(`\$release\s*=\s*'([^']+)';`)
	branchRegex := regexp.MustCompile(`\$branch\s*=\s*'([^']+)';`)
	maturityRegex := regexp.MustCompile(`\$maturity\s*=\s*([A-Z_]+);`)

	versionMatch := versionRegex.FindSubmatch(content)
	releaseMatch := releaseRegex.FindSubmatch(content)
	branchMatch := branchRegex.FindSubmatch(content)
	maturityMatch := maturityRegex.FindSubmatch(content)

	if versionMatch == nil || releaseMatch == nil || branchMatch == nil || maturityMatch == nil {
		return nil, errors.New("failed to parse moodle installation information")
	}

	version, err := strconv.ParseFloat(string(versionMatch[1]), 64)
	if err != nil {
		return nil, err
	}

	return &Moodle{
		Path:     path,
		Version:  version,
		Release:  string(releaseMatch[1]),
		Branch:   string(branchMatch[1]),
		Maturity: string(maturityMatch[1]),
	}, nil
}

func (moodle *Moodle) PrettyPrintMoodleInstallation() {
	fmt.Printf("Found moodle installation at %s\n\n", moodle.Path)
	fmt.Printf("Version: %.1f\n", moodle.Version)
	fmt.Printf("Release: %s\n", moodle.Release)
	fmt.Printf("Branch: %s\n", moodle.Branch)
	fmt.Printf("Maturity: %s\n\n", moodle.Maturity)
}

func (moodle *Moodle) GetVersionString() string {
	re := regexp.MustCompile(`\d+\.\d+\.\d+`)
	version := re.FindString(moodle.Release)
	return fmt.Sprintf("v%s", version)
}

func (moodle *Moodle) IsUsingGit() error {
	_, err := git.PlainOpen(moodle.Path)
	if err != nil {
		return fmt.Errorf("%s is not a git project", moodle.Path)
	}
	return nil
}

func (moodle *Moodle) GetGitTag() (string, error) {
	r, err := git.PlainOpen(moodle.Path)
	if err != nil {
		return "", fmt.Errorf("%s is not a git project", moodle.Path)
	}
	headRef, err := r.Head()
	if err != nil {
		return "", fmt.Errorf("Could not get HEAD of %s", moodle.Path)
	}

	tags, err := r.Tags()
	if err != nil {
		return "", fmt.Errorf("Could not get tags of %s", moodle.Path)
	}

	var tag *plumbing.Reference = nil
	tags.ForEach(func(tagRef *plumbing.Reference) error {
		obj, err := r.Object(plumbing.AnyObject, tagRef.Hash())
		if err != nil {
			return nil
		}

		var commitHash plumbing.Hash
		switch o := obj.(type) {
		case *object.Tag:
			commitHash = o.Target
		case *object.Commit:
			commitHash = o.Hash
		default:
			return nil
		}

		if commitHash == headRef.Hash() {
			tag = tagRef
		}
		return nil
	})

	if tag == nil {
		return "", fmt.Errorf("Could not get current tag of %s", moodle.Path)
	}

	return tag.Name().Short(), nil
}

func (moodle *Moodle) GetGitCommit() (string, error) {
	r, err := git.PlainOpen(moodle.Path)
	if err != nil {
		return "", fmt.Errorf("%s is not a git project", moodle.Path)
	}
	ref, err := r.Head()
	if err != nil {
		return "", fmt.Errorf("Could not get HEAD of %s", moodle.Path)
	}
	return ref.Hash().String()[:7], nil
}
