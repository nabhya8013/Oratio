package routes

import (
	"Oratio/PreSpeechLayer/handlers"

	"github.com/gin-gonic/gin"
)

func RegisterRoutes(r *gin.Engine) {
	// Existing
	r.POST("/session", handlers.GenerateAndStore)
	r.GET("/session", handlers.GetSessionByQuery)
	r.POST("/session/upload-audio", handlers.UploadAudio)

	// New: analyze by pulling audio from Supabase Storage
	r.POST("/session/analyze", handlers.AnalyzeSpeech)
}
