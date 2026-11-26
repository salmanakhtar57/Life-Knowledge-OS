
export function ProfileCard() {
  return (
    <section className="profile-section">
      <div className="profile-content">
        <div className="eyebrow">MY PERSONAL KNOWLEDGE SPACE</div>

        <h1>
          A place for
          <br />
          <span>everything I learn.</span>
        </h1>

        <p>
          I'm Salman — a Python developer, reader, and lifelong learner.
          Noteway brings together my writing, ideas, and things I've
          learned along the way.
        </p>

        <div className="profile-links">
          <a
            href="https://salm1.substack.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            Substack ↗
          </a>

          <span>·</span>

          <a
            href="https://medium.com/@salman1234"
            target="_blank"
            rel="noopener noreferrer"
          >
            Medium ↗
          </a>
        </div>
      </div>

      <div className="profile-decoration" aria-hidden="true">
        <span className="decoration-circle" />
        <span className="decoration-letter">N</span>
      </div>
    </section>
  );
}
