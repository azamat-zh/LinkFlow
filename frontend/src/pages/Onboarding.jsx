import { useEffect, useState } from "react";
import { getActors, uploadPDF } from "../api/client";
import ActorCard from "../components/ActorCard";
import FileDropzone from "../components/FileDropzone";

export default function Onboarding() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    getActors().then((actors) => setRecent(actors.slice(0, 5))).catch(() => {});
  }, [profile]);

  async function handleFileSelect(file) {
    setLoading(true);
    setError(null);
    setProfile(null);
    try {
      const result = await uploadPDF(file);
      setProfile(result);
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="two-col page-container">
      <div>
        <h2 className="page-title">Onboard an Actor</h2>
        <FileDropzone onFileSelect={handleFileSelect} isLoading={loading} error={error} />

        {profile && (
          <div style={{ marginTop: 24 }}>
            <div style={{ 
              background: "var(--teal-light)", 
              color: "var(--teal)", 
              padding: "12px 16px", 
              borderRadius: "var(--radius)", 
              marginBottom: 16,
              fontWeight: 600,
              fontSize: 14,
              border: "1px solid rgba(5, 150, 105, 0.2)"
            }}>
              ✓ Profile extracted successfully!
            </div>
            <ActorCard actor={profile} />
            <button className="btn" style={{ marginTop: 12 }} onClick={() => setProfile(null)}>
              Upload Another
            </button>
          </div>
        )}
      </div>

      <div>
        <h2 className="page-title">Recently Onboarded</h2>
        {recent.length === 0
          ? <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-muted)" }}>
              <div style={{ fontSize: 36, marginBottom: 8 }}>📂</div>
              <p>No actors onboarded yet.</p>
            </div>
          : (
            <div style={{ maxHeight: 650, overflowY: "auto", paddingRight: 8 }}>
              {recent.map((a) => <ActorCard key={a.id} actor={a} />)}
            </div>
          )
        }
      </div>
    </div>
  );
}