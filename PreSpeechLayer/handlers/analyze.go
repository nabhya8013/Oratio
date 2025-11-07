package handlers

import (
	"Oratio/PreSpeechLayer/services"
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"gorm.io/datatypes"
)

type AnalysisRequest struct {
	SessionID uint `json:"session_id" binding:"required"`
	// Optional: override storage source for this call
	AudioBucket string `json:"audio_bucket,omitempty"`
	AudioPath   string `json:"audio_path,omitempty"`
}

type PythonResponse struct {
	VadAsr struct {
		Transcription string `json:"transcription"`
	} `json:"vad_asr"`
}

// POST /session/analyze
// Pull audio from Supabase Storage (bucket/path), convert to WAV->base64, call Python, save results.
func AnalyzeSpeech(c *gin.Context) {
	var req AnalysisRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body", "detail": err.Error()})
		return
	}

	// Fetch the session
	session, err := services.GetSessionByID(req.SessionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	// Determine bucket/path to pull audio from
	bucket := req.AudioBucket
	path := req.AudioPath
	if bucket == "" {
		if session.AudioBucket != "" {
			bucket = session.AudioBucket
		} else {
			bucket = os.Getenv("SUPABASE_AUDIO_BUCKET")
		}
	}
	if path == "" {
		if session.AudioPath == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "No audio_path specified on request or session"})
			return
		}
		path = session.AudioPath
	}

	// 1) Download audio from Storage, 2) Convert to WAV if needed, 3) Base64 encode
	wavB64, err := services.GetMonoWavBase64FromStorage(c, bucket, path)
	if err != nil {
		c.JSON(http.StatusFailedDependency, gin.H{"error": "Failed to get audio from storage", "detail": err.Error()})
		return
	}

	// 4) Call Python unified_router /process_all
	pyURL := os.Getenv("PY_UNIFIED_ROUTER_URL")
	if pyURL == "" {
		pyURL = "http://localhost:8000"
	}
	// the router expects: session_id, audio_base64
	body := map[string]any{
		"session_id":   int(req.SessionID),
		"audio_base64": wavB64,
	}
	payload, _ := json.Marshal(body)

	resp, err := http.Post(pyURL+"/process_all", "application/json", bytes.NewBuffer(payload))
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Failed to reach Python unified router", "detail": err.Error()})
		return
	}
	defer resp.Body.Close()

	analysisBody, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read Python response"})
		return
	}
	if resp.StatusCode != http.StatusOK {
		log.Printf("Python returned %d: %s", resp.StatusCode, string(analysisBody))
		c.JSON(http.StatusFailedDependency, gin.H{"error": "Python error", "detail": string(analysisBody)})
		return
	}

	// Parse transcription (optional—it’s also in the blob)
	var pyResp PythonResponse
	if err := json.Unmarshal(analysisBody, &pyResp); err != nil {
		log.Printf("Failed to parse transcription: %v", err)
	}

	// Save to DB
	session.Transcript = pyResp.VadAsr.Transcription
	session.AnalysisResult = datatypes.JSON(analysisBody)
	if err := services.DB.Save(&session).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save analysis to DB"})
		return
	}

	c.Data(http.StatusOK, "application/json", analysisBody)
}
