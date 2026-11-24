import { useCallback, useRef, useState } from 'react';
import { ResourceLibrary } from './ResourceLibrary.jsx';
import { DashboardAmbient } from './DashboardAmbient.jsx';
import { DashboardArtwork } from './DashboardArtwork.jsx';
import { ProfilePage } from './ProfilePage.jsx';
import { UserSidebar } from './UserSidebar.jsx';
import { SchoolProfile } from './SchoolProfile.jsx';
import { UserDashboard } from './UserDashboard.jsx';
import { LearningLibrary } from './LearningLibrary.jsx';
import { useMobileLayout, usePortalDrawer } from './usePortalDrawer.js';
import logo from '../../assets/maxford-logo-wide.png';
import mark from '../../assets/maxford-mark.png';

export function UserPortal({ page = 'books', libraryRoute = [], onBookOpen }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const toggleRef = useRef(null);
  const sidebarRef = useRef(null), closeRef = useRef(null);
  const mobile = useMobileLayout();
  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);
  usePortalDrawer({ open: sidebarOpen, mobile, sidebarRef, closeRef, toggleRef, onClose: closeSidebar });
  const selectedPage = ['resources', 'profile', 'school', 'library'].includes(page) ? page : 'books';
  const hasLearningWorld = selectedPage === 'books' || selectedPage === 'library';
  const pageTitle = { books: 'Dashboard', library: 'Explore Books', school: 'School Profile', resources: 'Resources', profile: 'My Profile' }[selectedPage];
  return (
    <div className={`portal user-shell user-portal-shell${sidebarOpen ? ' sidebar-open' : ''}`}>
      {sidebarOpen && <>{mobile && <button className="portal-drawer-backdrop" type="button" tabIndex="-1" aria-label="Close sidebar" onClick={closeSidebar} />}<UserSidebar page={selectedPage === 'library' ? 'books' : selectedPage} onClose={closeSidebar} sidebarRef={sidebarRef} closeRef={closeRef} mobile={mobile} /></>}
      <div className="user-workspace" inert={mobile && sidebarOpen}>
      {hasLearningWorld && <div className="learning-world-scenery">
        <DashboardAmbient />
        <div className="mx-ground" aria-hidden="true"><DashboardArtwork variant="world-ground" /></div>
      </div>}
      <header className="portal-topline user-portal-header">
        <div className="user-header-start">
          <button className="user-sidebar-toggle" ref={toggleRef} type="button" aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'} title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'} aria-expanded={sidebarOpen} aria-controls="user-sidebar" onClick={() => setSidebarOpen(value => !value)}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" /></svg></button>
          <a className="user-header-logo" href="#/user/books" aria-label="Maxford Global Learning dashboard"><picture><source media="(max-width: 760px)" srcSet={mark} /><img src={logo} alt="" width="720" height="137" /></picture></a>
          <span className="user-header-breadcrumb"><span className="header-publisher">Maxford Global Learning <span aria-hidden="true">/</span> </span>{pageTitle}</span>
        </div>
        <nav aria-label="User account links">
          <a className="portal-textlink user-home-link" href="#/user/books" onClick={closeSidebar} aria-label="Home" aria-current={selectedPage === 'books' ? 'page' : undefined}><svg className="mobile-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="m3 11 9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1Z" /></svg><span className="user-header-link-text">Home</span></a>
          <a className="portal-textlink" href="#/user/resources" onClick={closeSidebar} aria-label="Resources" aria-current={selectedPage === 'resources' ? 'page' : undefined}><svg className="mobile-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M4 5h6l2 3h8v12H4Z" /></svg><span className="user-header-link-text">Resources</span></a>
          <a className="portal-textlink" href="#/user/library" onClick={closeSidebar} aria-label="E-Books" aria-current={selectedPage === 'library' ? 'page' : undefined}><svg className="mobile-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M12 6c-2-1.5-5-2-8-1.5V19c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V4.5C17 4 14 4.5 12 6Zm0 0v14.5" /></svg><span className="user-header-link-text">E-Books</span></a>
          <a className="portal-textlink" href="#/user/profile" onClick={closeSidebar} aria-label="Profile" aria-current={selectedPage === 'profile' ? 'page' : undefined}><svg className="mobile-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><circle cx="12" cy="8" r="4" /><path d="M4 22v-3a8 8 0 0 1 16 0v3" /></svg><span className="user-header-link-text">Profile</span></a>
        </nav>
      </header>
      <main className={`user-main${['school', 'library'].includes(selectedPage) ? ' user-school-main' : ''}`} key={selectedPage}>
        {selectedPage === 'school' ? <SchoolProfile /> :
          selectedPage === 'resources' ? <ResourceLibrary /> :
          selectedPage === 'profile' ? <ProfilePage /> :
          selectedPage === 'library' ? <LearningLibrary segments={libraryRoute} onBookOpen={onBookOpen} /> :
          <UserDashboard />}

      </main>
      <footer className="demo-notice user-footer"><span className="demo-dot" />Maxford Global <span>Interactive digital books for curious young minds.</span></footer>
      </div>
    </div>
  );
}
