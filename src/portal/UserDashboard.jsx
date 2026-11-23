import { useDemo } from './DemoContext.jsx';
import { ResourceOptions } from './ResourceOptions.jsx';
import { LearningScenery } from './LearningScenery.jsx';
import { DashboardArtwork, Sparkles } from './DashboardArtwork.jsx';

export function UserDashboard() {
  const { account, assignedBooks, progress } = useDemo();
  const position = progress[account.id];
  const continuedBook = position && assignedBooks.find(book => book.id === position.bookId);

  return (
    <div className="learning-dashboard">
      <LearningScenery />
      <section className="user-welcome mx-welcome">
        <div>
          <h1>
            <span className="mx-welcome-line">Welcome to <span className="mx-brand">Maxford!</span></span>
            <span className="mx-welcome-sub">A new day of learning and fun!</span>
          </h1>
        </div>
        <DashboardArtwork variant="welcome" />
        <Sparkles spots={[[58, 18, 16, 0], [64, 70, 12, 1.2], [96, 12, 14, .6], [52, 48, 10, 2]]} />
      </section>
      <a className="learning-entry portal-panel mx-ebooks" href="#/user/library">
        <span className="learning-entry-copy">
          <h2>Explore E-Books</h2>
          <span className="portal-muted">Discover interactive storybooks, activities, and learning resources.</span>
          <span className="learning-entry-count">{assignedBooks.length} book{assignedBooks.length === 1 ? '' : 's'} in your library</span>
        </span>
        <span className="mx-ebooks-arrow" aria-hidden="true">→</span>
        <DashboardArtwork variant="library" />
        <Sparkles spots={[[60, 20, 14, .3], [72, 74, 10, 1.4], [88, 16, 12, .9], [66, 44, 8, 2.1]]} />
        <span className="learning-entry-go" aria-hidden="true">→</span>
      </a>
      <ResourceOptions classFolders illustrated />
      {continuedBook && (
        <section className="continue-reading portal-panel">
          <img src={continuedBook.cover} alt="" />
          <div>
            <p className="portal-eyebrow">Continue Reading</p>
            <h2>{continuedBook.title}</h2>
            <p className="portal-muted">Page {position.page} of {continuedBook.pages.length} · This session</p>
          </div>
          <a className="portal-primary" href={`#/book/${encodeURIComponent(continuedBook.id)}/read/${position.page}`}>Continue reading →</a>
        </section>
      )}
      <DashboardArtwork variant="landscape" />
    </div>
  );
}
