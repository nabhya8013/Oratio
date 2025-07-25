package utils

import "strings"

// CleanGeminiOutput strips code block formatting and trims the JSON
func CleanGeminiOutput(s string) string {
	s = strings.TrimSpace(s)

	// Remove triple backticks
	if strings.HasPrefix(s, "```json") {
		s = strings.TrimPrefix(s, "```json")
	}
	if strings.HasPrefix(s, "```") {
		s = strings.TrimPrefix(s, "```")
	}
	if strings.HasSuffix(s, "```") {
		s = strings.TrimSuffix(s, "```")
	}
	return strings.TrimSpace(s)
}
