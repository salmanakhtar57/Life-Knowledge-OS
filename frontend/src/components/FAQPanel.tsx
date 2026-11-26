
// import { useEffect, useState, type FormEvent } from "react";
// import {
//   ApiError,
//   uploadDocument,
// } from "../api/client";

// function formatDate(value: string): string {
//   return new Intl.DateTimeFormat("en", {
//     day: "numeric",
//     month: "short",
//     year: "numeric",
//   }).format(new Date(value));
// }

// export function FAQPanel() {
//   const [documents, setDocuments] = useState<DocumentListItem[]>([]);
//   const [file, setFile] = useState<File | null>(null);
//   const [loading, setLoading] = useState(false);
//   const [uploading, setUploading] = useState(false);
//   const [message, setMessage] = useState("");
//   const [error, setError] = useState("");

//   async function loadDocuments() {
//     setLoading(true);
//     setError("");

//     try {
//       const token = localStorage.getItem("access_token") ?? undefined;
//       setDocuments(await getDocuments(token));
//     } catch (err) {
//       setError(
//         err instanceof ApiError
//           ? err.message
//           : "Could not load your documents.",
//       );
//     } finally {
//       setLoading(false);
//     }
//   }

//   async function handleUpload(event: FormEvent<HTMLFormElement>) {
//     event.preventDefault();

//     if (!file || uploading) return;

//     setUploading(true);
//     setMessage("");
//     setError("");

//     try {
//       const result = await uploadDocument(file);

//       setMessage(
//         `Added "${result.title}" with ${result.chunk_count} chunks.`,
//       );

//       setFile(null);
//       await loadDocuments();
//     } catch (err) {
//       setError(
//         err instanceof ApiError ? err.message : "Could not upload the file.",
//       );
//     } finally {
//       setUploading(false);
//     }
//   }

//   useEffect(() => {
//     void loadDocuments();
//   }, []);

//   return (
//     <section className="faq-section">
//       <div className="section-heading">
//         <div>
//           <div className="eyebrow">PERSONAL KNOWLEDGE</div>
//           <h2>My pages & notes.</h2>
//           <p>Documents that feed your personal knowledge base.</p>
//         </div>

//         <button
//           type="button"
//           className="text-button"
//           onClick={loadDocuments}
//           disabled={loading}
//         >
//           Refresh ↻
//         </button>
//       </div>

//       <form className="faq-upload" onSubmit={handleUpload}>
//         <div>
//           <strong>Add a personal document</strong>
//           <p>Upload a .txt or .md file to your knowledge base.</p>
//         </div>

//         <div className="faq-upload-controls">
//           <input
//             type="file"
//             accept=".txt,.md"
//             onChange={(event) =>
//               setFile(event.target.files?.[0] ?? null)
//             }
//             disabled={uploading}
//           />

//           <button type="submit" disabled={!file || uploading}>
//             {uploading ? "Uploading…" : "Upload"}
//           </button>
//         </div>
//       </form>

//       {message && <p className="success-message">{message}</p>}
//       {error && <p className="inline-error">{error}</p>}

//       <div className="document-list">
//         {loading ? (
//           <p className="muted-text">Loading documents…</p>
//         ) : documents.length === 0 ? (
//           <p className="muted-text">
//             No accessible documents found. Upload a document to get started.
//           </p>
//         ) : (
//           documents.map((document) => (
//             <article className="document-item" key={document.id}>
//               <div>
//                 <strong>{document.title}</strong>
//                 <span>Added {formatDate(document.created_at)}</span>
//               </div>
//               <span className="document-type">DOCUMENT</span>
//             </article>
//           ))
//         )}
//       </div>
//     </section>
//   );
// }
