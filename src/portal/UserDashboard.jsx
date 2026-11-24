import { useDemo } from './DemoContext.jsx';
import { resourceLinks } from '../data/resourceLinks.js';
import { DashboardArtwork, Sparkles } from './DashboardArtwork.jsx';

// The dashboard (design: assets/maxford-dashboard-3.jpg): a wide picture banner of a learning world, then one
// row of five cards (E-Books and the four resources), each with its picture, icon, words and button, over a
// scenery of books, a globe and a school bag. The pictures are crops of the design; all words and links are live.
const COLOURS = { ebooks: 'purple', dropbox: 'yellow', 'paper-maker': 'blue', 'resources-app': 'pink', 'school-management': 'green' };

function WorldCard({ id, title, text, action, href, external, pending, extra, index }) {
  const body = <>
    <span className="mx-card-art"><DashboardArtwork variant={`world-${id}`} /></span>
    <span className="mx-card-body">
      <span className="mx-card-title"><DashboardArtwork variant={`world-icon-${id}`} /><h2>{title}</h2></span>
      <span className="mx-card-text">{text}</span>
      {extra && <span className="mx-card-extra">{extra}</span>}
      <span className="mx-card-button">{pending ? 'Link coming soon' : <>{action} <span aria-hidden="true">{external ? '↗' : '→'}</span></>}</span>
    </span>
  </>;
  const cls = `mx-card mx-card-${COLOURS[id]}${pending ? ' pending' : ''}`;
  const style = { animationDelay: `${.15 + index * .09}s` };
  return pending
    ? <article className={cls} style={style}>{body}</article>
    : <a className={cls} style={style} href={href} target={external ? '_blank' : undefined} rel={external ? 'noopener noreferrer' : undefined}>{body}</a>;
}

export function UserDashboard() {
  const { account, assignedBooks, progress } = useDemo();
  const position = progress[account.id];
  const continuedBook = position && assignedBooks.find(book => book.id === position.bookId);
  const cards = [
    { id: 'ebooks', title: 'E-Books', text: 'Read, explore and learn with digital books.', action: 'Explore E-Books', href: '#/user/library',
      extra: `${assignedBooks.length} book${assignedBooks.length === 1 ? '' : 's'} in your library` },
    ...resourceLinks.map(resource => {
      const internal = resource.id === 'dropbox';
      const available = internal || /^https?:\/\//i.test(resource.url);
      return { id: resource.id, title: resource.title, text: resource.description, action: resource.action || 'Open',
        href: internal ? '#/user/resources' : resource.url, external: !internal, pending: !available };
    })
  ];

  return (
    <div className="learning-dashboard mx-world">
      <section className="mx-hero" aria-labelledby="mx-hero-title">
        <DashboardArtwork variant="world-hero" />
        <h1 id="mx-hero-title" className="mx-visually-hidden">Welcome to your learning world: read, explore, practise, create and grow</h1>
        <Sparkles spots={[[33, 22, 18, 0], [67, 18, 14, .8], [50, 82, 12, 1.6], [24, 70, 12, 2.2], [78, 64, 14, 1.1], [95, 14, 16, .4]]} />
      </section>
      <div className="mx-cards">
        {cards.map((card, index) => <WorldCard key={card.id} index={index} {...card} />)}
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
      <div className="mx-ground" aria-hidden="true"><DashboardArtwork variant="world-ground" /></div>
    </div>
  );
}
