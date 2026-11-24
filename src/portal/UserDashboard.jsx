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
      {/* the board (design: assets/maxford-dashboard-2.jpg): a tall welcome card on the left; on the right the
          E-Books banner over the four resource cards, the school portal card running down the side */}
      <div className="mx-board">
        <section className="user-welcome mx-welcome">
          <div>
            <h1>
              <span className="mx-welcome-line"><span className="mx-hello">Welcome to</span> <span className="mx-brand">Maxford!</span></span>
              <span className="mx-welcome-sub">A new day of <span className="mx-warm">learning</span> and <span className="mx-warm">fun!</span></span>
            </h1>
          </div>
          <DashboardArtwork variant="board-welcome" />
          <Sparkles spots={[[14, 36, 16, 0], [86, 44, 12, 1.2], [8, 70, 14, .6], [90, 72, 10, 2], [50, 30, 12, 1.6]]} />
        </section>
        <a className="learning-entry portal-panel mx-ebooks" href="#/user/library">
          <span className="learning-entry-copy">
            <h2>Explore E-Books</h2>
            <span className="portal-muted">Discover interactive storybooks, activities, and learning resources.</span>
            <span className="learning-entry-count">{assignedBooks.length} book{assignedBooks.length === 1 ? '' : 's'} in your library</span>
          </span>
          <DashboardArtwork variant="board-library" />
          <Sparkles spots={[[52, 22, 14, .3], [66, 74, 10, 1.4], [82, 16, 12, .9], [58, 50, 8, 2.1]]} />
          <span className="learning-entry-go" aria-hidden="true">→</span>
        </a>
        <ResourceOptions showHeading={false} classFolders illustrated art="-2" />
        <a className="mx-class-pill" href="#/user/resources">View class resources <span aria-hidden="true">→</span></a>
      </div>
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
