package ApplicationLayer

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "your_project/models"
    "golang.org/x/sync/errgroup"
)

func ProcessSession(audioPath, idealAnswer string) (*models.Session, error) {
    session := &models.Session{
        AudioPath:   audioPath,
    }

    ctx := context.Background()
    g, ctx := errgroup.WithContext(ctx)

    // Channels to receive results
    vadCh := make(chan models.VADResult, 1)
    featCh := make(chan models.FeatureResult, 1)
    serCh := make(chan models.SERResult, 1)
    simCh := make(chan models.SimilarityResult, 1)

    // VAD + ASR
    g.Go(func() error {
        result, err := callVADASR(audioPath)
        if err != nil {
            return err
        }
        vadCh <- result
        return nil
    })

    // Features
    g.Go(func() error {
        result, err := callFeatures(audioPath)
        if err != nil {
            return err
        }
        featCh <- result
        return nil
    })

    // SER
    g.Go(func() error {
        result, err := callSER(audioPath)
        if err != nil {
            return err
        }
        serCh <- result
        return nil
    })

    // Similarity
    g.Go(func() error {
        // Wait for vad result
        vad := <-vadCh
        result, err := callSimilarity(vad.Transcription, idealAnswer)
        if err != nil {
            return err
        }
        simCh <- result
        return nil
    })

    // Wait for all to finish
    if err := g.Wait(); err != nil {
        return nil, err
    }

    // Collect results
    vad := <-vadCh
    feat := <-featCh
    ser := <-serCh
    sim := <-simCh

    session.StartTime = vad.StartTime
    session.Transcription = vad.Transcription
    session.PitchMean = feat.PitchMean
    session.PitchStd = feat.PitchStd
    session.RMSMean = feat.RMSMean
    session.RMSStd = feat.RMSStd
    session.EmotionLabel = ser.Label
    session.EmotionScore = ser.Score
    session.SimilarityScore = sim.Similarity

    return session, nil
}
