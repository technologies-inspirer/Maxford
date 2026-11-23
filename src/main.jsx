import { createRoot } from 'react-dom/client';
import { LoadingScreen } from './loading/LoadingScreen.jsx';
import '../data.js';
import '../books/library.js';
import '../books/zones.js';
import '../books/activities.js';
import '../styles.css';
import './theme.css';

const root = createRoot(document.getElementById('root'));
root.render(<LoadingScreen />);

// Each book's activities live in their own file (books/activities-<book>.js, written by tools/make_<book>.py).
// Add an import for a new book here; docs/adding-a-book.md lists the steps.
async function startApp() {
  const minimumStartup = new Promise(resolve => setTimeout(resolve, 1000));   // the owl shows briefly, not for long
  await Promise.all([
    import('../books/activities-maxford.js'),
    import('../books/game-crops.js'),
    import('../books/questions.js'),
    import('../books/questions-maxford.js'),
    import('../books/questions-maxford-maths.js')
  ]);
  const { App } = await import('./App.jsx');
  await minimumStartup;
  root.render(<App />);
}

startApp().catch(error => {
  console.error('Could not load the interactive book data.', error);
  root.render(<p role="alert">Could not load the book data. Refresh the page or check the network connection.</p>);
});
