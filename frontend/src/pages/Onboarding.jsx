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
    <div className="two-col" style={{ padding: "2rem" }}>
      <div>
        <h2 style={{ marginTop: 0 }}>Onboard an Actor</h2>
        <FileDropzone onFileSelect={handleFileSelect} isLoading={loading} error={error} />

        {profile && (
          <div style={{ marginTop: 20 }}>
            <p style={{ color: "var(--teal)", fontWeight: 600, marginBottom: 8 }}>
              Profile extracted successfully!
            </p>
            <ActorCard actor={profile} />
            <button className="btn" style={{ marginTop: 8 }} onClick={() => setProfile(null)}>
              Upload Another
            </button>
          </div>
        )}
      </div>

      <div>
        <h2 style={{ marginTop: 0 }}>Recently Onboarded</h2>
        {recent.length === 0
          ? <p style={{ color: "var(--text-muted)" }}>No actors onboarded yet.</p>
          : (
            <div style={{ maxHeight: 600, overflowY: "auto" }}>
              {recent.map((a) => <ActorCard key={a.id} actor={a} />)}
            </div>
          )
        }
      </div>
    </div>
  );
}
