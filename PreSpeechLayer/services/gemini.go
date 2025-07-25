package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"

	"strings"

	"google.golang.org/genai"
)

type Question struct {
	NpcID int    `json:"npc_id"`
	Text  string `json:"text"`
}

type SpeechData struct {
	Speech    string     `json:"speech"`
	Questions []Question `json:"questions"`
}

func ParseGeminiResult(raw string) (*SpeechData, error) {
	start := strings.Index(raw, "```json")
	end := strings.LastIndex(raw, "```")

	if start == -1 || end == -1 || end <= start {
		return nil, errors.New("invalid JSON block")
	}

	jsonString := raw[start+7 : end] // skip "```json\n"
	jsonString = strings.TrimSpace(jsonString)

	var result SpeechData
	if err := json.Unmarshal([]byte(jsonString), &result); err != nil {
		return nil, err
	}

	return &result, nil
}

func Gemini(PaperBody string) (*SpeechData, error) {
	ctx := context.Background()
	// The client gets the API key from the environment variable `GEMINI_API_KEY`.
	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}
	prompt := `You are an academic assistant. Given a research paper, do the following:

		1. Summarize the core message into a clear, spoken-style presentation of approximately 3 minutes.
		2. Generate 10–15 challenging audience questions that could be asked during the talk.
		3. Assign a random npc_id between 1 and 20 to each question.
		4. Return the result strictly in this JSON format (with no explanations or markdown):

		{
		"speech": "<speech_text_here>",
		"questions": [
			{ "npc_id": <int>, "text": "<question_1>" },
			{ "npc_id": <int>, "text": "<question_2>" }
			 ...
			{ "npc_id": <int>, "text": "<question_n>" }
		]
		}`

	result, err := client.Models.GenerateContent(
		ctx,
		"gemini-2.5-flash",
		genai.Text(prompt+PaperBody),
		nil,
	)
	if err != nil {
		log.Fatal(err)
	}

	raw := result.Text() // this is the big string
	parsed, err := ParseGeminiResult(raw)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Speech:", parsed.Speech)

	return parsed, err
}
