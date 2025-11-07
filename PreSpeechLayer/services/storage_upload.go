package services

import (
	"Oratio/PreSpeechLayer/models"
	"bytes"
	"context"
	"fmt"
	"net/http"
	"os"
)

func UploadToStorage(ctx context.Context, bucket, path string, data []byte) error {
	baseURL := os.Getenv("SUPABASE_URL")
	svcKey := os.Getenv("SUPABASE_SERVICE_KEY")

	url := fmt.Sprintf("%s/storage/v1/object/%s/%s", baseURL, bucket, path)

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(data))
	if err != nil {
		return err
	}

	req.Header.Set("Authorization", "Bearer "+svcKey)
	req.Header.Set("Content-Type", "application/octet-stream")
	req.Header.Set("apikey", svcKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 300 {
		return fmt.Errorf("upload failed %s", resp.Status)
	}

	return nil
}

func UpdateSessionAudio(sessionID uint, bucket, path string) error {
	return DB.Model(&models.Session{}).Where("id = ?", sessionID).
		Updates(map[string]interface{}{
			"audio_bucket": bucket,
			"audio_path":   path,
		}).Error
}
