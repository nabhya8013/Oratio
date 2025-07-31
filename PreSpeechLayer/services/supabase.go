package services

import (
	"Oratio/models"
	"log"
	"os"

	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDatabase() {
	err := godotenv.Load()
	if err != nil {
		log.Println("Warning: .env file not found, using system env")
	}

	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		log.Fatal("❌ DATABASE_URL not found in env")
	}

	db, err := gorm.Open(postgres.New(postgres.Config{
		DSN:                  dsn,
		PreferSimpleProtocol: true,
	}), &gorm.Config{})
	if err != nil {
		log.Fatalf("❌ Failed to connect to Supabase DB: %v", err)
	}

	log.Println("✅ Connected to Supabase PostgreSQL!")
	DB = db

	// Auto-migrate models (replace with your actual model structs)
	err = db.AutoMigrate(
		&models.Session{},
		&models.Question{},
		
	)
	if err != nil {
		log.Fatalf("❌ Migration failed: %v", err)
	}
}
