
export function MediumPanel() {
  return (
    <section className="publication-card medium-card">
      <div className="publication-heading">
        <div>
          <div className="eyebrow">THE WRITING DESK · 02</div>
          <h2>Latest on Medium</h2>
          <p>A second home for my writing.</p>
        </div>

        <span className="publication-icon medium-icon">M</span>
      </div>

      <div className="medium-placeholder">
        <div className="placeholder-symbol">M.</div>
        <h3>Coming into focus.</h3>
        <p>
          My Medium articles will live here once the integration
          is ready.
        </p>
        <span className="coming-soon">INTEGRATION PLANNED</span>
      </div>

      <div className="publication-actions">
        <a
          href="https://medium.com/@salman1234"
          target="_blank"
          rel="noopener noreferrer"
          className="text-button"
        >
          Visit Medium ↗
        </a>
      </div>
    </section>
  );
}
