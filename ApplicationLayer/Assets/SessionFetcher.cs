using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace OratioAPI
{
    [Serializable]
    public class SessionQuestion
    {
        public string text;
        public int npc_id;
    }

    [Serializable]
    public class SessionData
    {
        public int id;
        public string speech;
        public List<SessionQuestion> questions;
        public string created_by;
        public string generated_by;
        public string created_at;
    }
}

public class SessionFetcher : MonoBehaviour
{
    [SerializeField] private string apiUrl = "http://yourserver.com/session"; // Replace with actual API URL
    [SerializeField] private int sessionId = 2;

    [Header("Fetched Data")]
    public string Speech;
    public List<string> Questions = new List<string>();

    void Start()
    {
        StartCoroutine(FetchSession(sessionId));
    }

    IEnumerator FetchSession(int id)
    {
        string url = $"{apiUrl}?id={id}";
        using UnityWebRequest request = UnityWebRequest.Get(url);
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError ||
            request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"API Error: {request.responseCode} - {request.error}");
        }
        else
        {
            string json = request.downloadHandler.text;
            OratioAPI.SessionData session = JsonUtility.FromJson<OratioAPI.SessionData>(json);

            // Assign values to public fields
            Speech = session.speech;
            Questions.Clear();
            foreach (var q in session.questions)
            {
                Questions.Add(q.text);
            }

            // Debug log (optional)
            Debug.Log($"Speech: {Speech}");
            foreach (string question in Questions)
            {
                Debug.Log($"Question: {question}");
            }
        }
    }
}
