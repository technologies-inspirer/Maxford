import { useState } from 'react';
import { DEMO_CREDENTIALS } from './demoStore.js';
import { useDemo } from './DemoContext.jsx';
import { Feedback, Logo, PasswordField } from './Shared.jsx';
import { DashboardAmbient } from './DashboardAmbient.jsx';
import { DashboardArtwork, Sparkles } from './DashboardArtwork.jsx';

// the three Play Group books, by their own covers (books/<id>/cover.jpg)
const LOGIN_BOOKS = [
  ['maxford-global-qaida-3-english', 'Simply Phonics Step A'],
  ['maxford-global-qaida-3-maths', 'Simply Maths Step A'],
  ['maxford-global-qaida-3-urdu', 'آسان اردو قدم پہلا']
];

function LoginBooks() {
  return <div className="login-shelf">{LOGIN_BOOKS.map(([id, title], index) =>
    <figure key={id} className={`login-book login-book-${index + 1}`}>
      <img src={`books/${id}/cover.jpg`} alt={title} width="720" height="913" />
      <span className="login-book-shine" aria-hidden="true" />
    </figure>)}
  </div>;
}

export function LoginPage() {
  const { store } = useDemo();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(null);
  const submit = event => {
    event.preventDefault();
    try {
      const role = store.signIn(email, password);
      setPassword('');
      location.hash = role === 'admin' ? '#/admin/overview' : '#/user/books';
    } catch (error) { setMessage({ error: true, text: error.message }); setPassword(''); }
  };
  return <div className="portal login-screen"><DashboardAmbient /><div className="login-top"><Logo colour /></div><main className="login-layout"><section className="login-story"><p className="portal-eyebrow">Interactive digital books</p><h1>Learning that<br /><em>comes alive!</em></h1><p className="login-description">Open a book. Discover a new world. Read, listen, play and create with a library made for curious young minds.</p><div className="login-artwork" role="img" aria-label="The books Simply Phonics, Simply Maths and Aasan Urdu"><LoginBooks /><Sparkles spots={[[14, 12, 16, 0], [52, 4, 14, .9], [86, 18, 12, 1.6], [30, 30, 10, 2.2], [70, 34, 10, .5]]} /></div><p className="login-caption">Big discoveries start with a little curiosity.</p></section><div className="login-panel-wrap"><span className="login-deco" aria-hidden="true"><DashboardArtwork variant="login-cloud" /><DashboardArtwork variant="login-butterfly" /><DashboardArtwork variant="login-star" /><DashboardArtwork variant="login-butterfly-2" /></span><section className="login-panel portal-panel" aria-labelledby="login-heading"><span className="portal-pill">Your learning space</span><h2 id="login-heading">Welcome back</h2><p className="portal-muted">Sign in to explore your books and resources.</p><form onSubmit={submit}><label className="portal-field" htmlFor="login-email">Email<input id="login-email" name="email" type="email" autoComplete="username" value={email} onChange={event => setEmail(event.target.value)} required placeholder="you@example.com" /><svg className="login-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="2.5" /><path d="m4 7 8 6 8-6" /></svg></label><PasswordField id="login-password" value={password} onChange={setPassword} autoComplete="current-password" minLength={1} /><Feedback message={message} /><button className="portal-primary full" type="submit">Sign in <span aria-hidden="true">→</span></button></form><p className="login-help">Need an account or password reset?<br />Contact your administrator.</p><div className="demo-credentials"><h3>Start exploring</h3><div className="credential-row"><b>Reader</b><span>{DEMO_CREDENTIALS.user.email}</span><code>{DEMO_CREDENTIALS.user.password}</code></div></div></section></div></main><span className="login-deco-corner" aria-hidden="true"><DashboardArtwork variant="login-cloud-2" /></span></div>;
}
