package services

import (
	"bytes"
	"context"
	"encoding/base64"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func DownloadFromStorage(ctx context.Context, bucket, path string) ([]byte, error) {
	baseURL := os.Getenv("SUPABASE_URL")
	svcKey := os.Getenv("SUPABASE_SERVICE_KEY")
	if baseURL == "" || svcKey == "" {
		return nil, fmt.Errorf("Supabase URL or service key not set")
	}

	url := fmt.Sprintf("%s/storage/v1/object/%s/%s", baseURL, bucket, path)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+svcKey)
	req.Header.Set("apikey", svcKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("storage download failed: %s - %s", resp.Status, string(b))
	}

	return io.ReadAll(resp.Body)
}

func ConvertToMonoWav(input []byte, srcExt string) ([]byte, error) {
	ffmpeg := os.Getenv("FFMPEG_BIN")
	if ffmpeg == "" {
		ffmpeg = "ffmpeg"
	}

	tmpDir := os.TempDir()
	inFile := filepath.Join(tmpDir, "input."+srcExt)
	outFile := filepath.Join(tmpDir, "output.wav")

	if err := os.WriteFile(inFile, input, 0644); err != nil {
		return nil, err
	}
	defer os.Remove(inFile)
	defer os.Remove(outFile)

	cmd := exec.Command(
		ffmpeg,
		"-y",
		"-i", inFile,
		"-ac", "1", // ✅ force mono
		"-ar", "16000", // ✅ 16 kHz
		"-sample_fmt", "s16", // ✅ 16-bit PCM
		outFile,
	)

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("ffmpeg error: %v | %s", err, stderr.String())
	}

	return os.ReadFile(outFile)
}

func GetMonoWavBase64FromStorage(ctx context.Context, bucket, path string) (string, error) {
	ext := "wav"
	if dot := filepath.Ext(path); len(dot) > 1 {
		ext = dot[1:]
	}

	original, err := DownloadFromStorage(ctx, bucket, path)
	if err != nil {
		return "", err
	}

	// If already WAV, still convert to enforce mono PCM16
	wavBytes, err := ConvertToMonoWav(original, ext)
	if err != nil {
		return "", err
	}

	return base64.StdEncoding.EncodeToString(wavBytes), nil
}
