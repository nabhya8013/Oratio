package main

import (
	"log"
	"os"

	"Oratio/PreSpeechLayer/routes"
	"Oratio/PreSpeechLayer/services"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {

	// ✅ Load .env automatically (if present)
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	// ✅ Validate required env vars
	required := []string{
		"DATABASE_URL",
		"SUPABASE_URL",
		"SUPABASE_SERVICE_KEY",
	}

	for _, key := range required {
		if os.Getenv(key) == "" {
			log.Fatalf("❌ Environment variable %s is missing. Backend cannot start.", key)
		}
	}

	// ✅ Initialize database connection
	services.InitDatabase()
	log.Println("✅ Connected to Supabase Postgres successfully.")

	// ✅ Initialize Gin router
	r := gin.Default()

	// ✅ Register API routes
	routes.RegisterRoutes(r)

	// ✅ Start server
	log.Println("🚀 PreSpeechLayer backend running on http://localhost:8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("❌ Failed to start server: %v", err)
	}
}
