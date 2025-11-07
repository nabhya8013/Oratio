package handlers

import (
	"context"
	"encoding/base64"
	"fmt"
	"net/http"
	"time"

	"Oratio/PreSpeechLayer/services"

	"github.com/gin-gonic/gin"
)

type UploadAudioRequest struct {
	SessionID   uint   `json:"session_id"`
	AudioBase64 string `json:"audio_base64"`
	FileExt     string `json:"file_ext"` // "wav", "mp3", "webm" etc.
}

func UploadAudio(c *gin.Context) {
	var req UploadAudioRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid body", "detail": err.Error()})
		return
	}

	// Decode base64
	audioBytes, err := base64.StdEncoding.DecodeString(req.AudioBase64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid base64 audio"})
		return
	}

	// Storage bucket name
	bucket := "recordings"

	// File path: session_12_1699219192.wav
	filename := fmt.Sprintf("session_%d_%d.%s", req.SessionID, time.Now().Unix(), req.FileExt)
	storagePath := filename

	// Upload to Supabase storage
	ctx := context.Background()
	err = services.UploadToStorage(ctx, bucket, storagePath, audioBytes)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed storage upload", "detail": err.Error()})
		return
	}

	// Update session row
	err = services.UpdateSessionAudio(req.SessionID, bucket, storagePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update session", "detail": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "uploaded",
		"bucket": bucket,
		"path":   storagePath,
	})
}
