import { useState } from 'react';
import { unlockBooks } from '../bookLock.js';
import { Logo, SignOut } from './Shared.jsx';

// Asked once on a device after sign-in: the books' pages are locked on the site (tools/lock_books.py) and open
// only with the book password the publisher gives to schools.
export function BookUnlock({ onUnlocked }) {
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [wrong, setWrong] = useState(false);
  const submit = async event => {
    event.preventDefault();
    setBusy(true); setWrong(false);
    try {
      if (await unlockBooks(password.trim())) onUnlocked();
      else setWrong(true);
    } catch {
      setWrong(true);
    }
    setBusy(false);
  };
  return <div className="portal login-screen book-unlock-screen">
    <div className="login-top"><Logo colour /></div>
    <main className="book-unlock">
      <section className="login-panel portal-panel" aria-labelledby="book-unlock-heading">
        <span className="portal-pill">Your books</span>
        <h2 id="book-unlock-heading">Book password</h2>
        <p className="portal-muted">Enter the book password from your school to open the books on this device. You will be asked only once.</p>
        <form onSubmit={submit}>
          <label className="portal-field" htmlFor="book-password">Book password
            <input id="book-password" type="password" autoComplete="off" value={password} onChange={event => setPassword(event.target.value)} required autoFocus />
          </label>
          {wrong && <p className="portal-feedback error" role="alert">That password does not open the books. Please check it and try again.</p>}
          <button className="portal-primary full" type="submit" disabled={busy || !password.trim()}>{busy ? 'Opening…' : 'Open my books'} <span aria-hidden="true">→</span></button>
        </form>
        <p className="login-help">No password? Ask your school or Maxford Global.</p>
        <SignOut />
      </section>
    </main>
  </div>;
}
