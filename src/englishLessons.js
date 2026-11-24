// The letter (or number) lesson bar of the Play Group, Nursery and Prep books: a side button for each
// letter that opens its lesson page, the publisher's Story/Vocabulary video, the picture game and the tracing.
//
// Add a book here when it has one lesson per letter or number:
//   'book-id': { subject: 'English', kind: 'Letter' }                 lessons found from the book's Story / Vocabulary
//                                                                     video buttons ("Story of letter Aa", "Story: بے")
//   'book-id': { subject: 'English', kind: 'Letter', pages: [5, 7] }  lessons on these pages, one letter each from a,
//                                                                     with tracing on the next page (as in English 3+)
const LESSON_BOOKS = {
  // Play Group (3+): each letter's or number's "Sound" / "Introduction" page; its writing page is the next one
  'maxford-global-qaida-3-english': {
    subject: 'English',
    kind: 'Letter',
    pages: [11, 15, 19, 23, 31, 35, 39, 43, 49, 53, 57, 61, 69, 73, 77, 81, 87, 91, 95, 99, 107, 111, 115, 119, 125, 129]
  },
  'maxford-global-qaida-3-maths': {
    subject: 'Maths',
    kind: 'Number',
    // 0 to 20, as the contents page lists them (printed page - 1: the blank first page of the PDF is left out)
    pages: [55, 9, 13, 17, 21, 27, 33, 39, 43, 47, 57, 65, 68, 71, 74, 77, 84, 87, 90, 93, 96]
  },
  'maxford-global-qaida-3-urdu': {
    subject: 'Urdu',
    kind: 'Letter',
    pages: [11, 15, 20, 24, 27, 30, 33, 40, 43, 46, 49, 56, 59, 62, 65, 68, 71, 74, 81, 84, 87, 90, 97, 100, 103, 106, 113, 116, 119,
      122, 125, 128, 135, 138, 141, 144, 147],
    labels: [...'اآبپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہء', 'ی، ے']
  },
  'maxford-global-qaida-4-english': {
    subject: 'English',
    kind: 'Letter',
    pages: [6, 10, 14, 18, 24, 28, 32, 36, 42, 46, 50, 54, 60, 64, 68, 72, 78, 82, 86, 90, 94, 100, 104, 108, 112, 116]
  },
  'maxford-global-qaida-4-maths': {
    subject: 'Maths',
    kind: 'Number',
    pages: [27, 5, 7, 9, 11, 13, 19, 21, 23, 25, 29, 45, 47, 49, 51, 53, 59, 61, 63, 65, 67]
  },
  'maxford-global-qaida-4-urdu': {
    subject: 'Urdu',
    kind: 'Letter',
    pages: [4, 6, 10, 13, 16, 19, 22, 29, 32, 35, 38, 45, 47, 49, 51, 53, 55, 57, 63, 66, 69, 72, 75, 77, 83, 86, 89, 92, 95, 98, 104, 107, 110, 113, 115, 118, 120],
    labels: [...'اآبپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہء', 'ی، ے']
  }
};

const acts = (book, page) => book.pages[page - 1]?.acts || [];
const lessonVideo = (book, page) => {
  const qrVideos = book.pages[page - 1]?.qr?.videos || [];
  return qrVideos.find(video => /for students/i.test(video.title)) || qrVideos[0] || null;
};
const storyVideo = activities => {
  const story = ['story', 'vocabulary'].map(label => activities.find(activity => activity.type === 'videos' && (activity.label || '').toLowerCase() === label)).find(Boolean);
  const id = story?.videos?.[0]?.src?.match(/(?:youtu\.be\/|[?&]v=)([\w-]{11})/)?.[1];
  return id ? { id, title: story.title } : null;
};
const nameOf = activity => (activity.title || '').replace(/^(story|vocabulary)(\s+of\s+letter)?\s*:?\s*/i, '').replace(/^number\s+/i, '').trim();

// Reuse the book's real lessons, videos and games. No separate copy of lesson content.
// Each lesson: key (unique), name ("Gg", "5", "بے"), big/small (side button), kind, page, tracePage, videos, game, trace.
export function englishLessons(book) {
  const config = LESSON_BOOKS[book.id];
  if (!config) return [];
  if (config.pages) return config.pages.map((page, index) => {
    const activities = acts(book, page);
    const game = activities.find(activity => activity.type === 'game');
    const isNumber = config.kind === 'Number';
    const label = config.labels?.[index] ?? (isNumber ? String(index) : null);
    const letter = label ?? String.fromCharCode(97 + index);
    const tracePage = isNumber && index === 0 ? page : page + 1;
    return {
      letter, key: letter, name: label ?? (letter.toUpperCase() + letter), big: letter.toUpperCase(), small: label ? '' : letter, kind: config.kind, subject: config.subject,
      page, tracePage,
      words: (game?.targets || []).map(target => target.name), game,
      lessonVideo: lessonVideo(book, page),
      story: activities.find(activity => activity.type === 'story'),
      // its videos, with those on its writing page (the Formation video sits there in the Play Group books)
      videos: [...activities, ...(tracePage !== page ? acts(book, tracePage) : [])].filter(activity => activity.type === 'videos'),
      trace: acts(book, tracePage).find(activity => activity.type === 'fill')
    };
  });
  const lessons = [];
  book.pages.forEach((_, index) => {
    const page = index + 1;
    const intro = acts(book, page).find(activity => activity.type === 'videos' && /^(story|vocabulary)$/i.test(activity.label || ''));
    const name = intro && nameOf(intro);
    if (!name || lessons.some(lesson => lesson.name === name)) return;
    // the writing page is this page if it has its own tracing, otherwise the next page when that is not another lesson
    const next = acts(book, page + 1);
    const nextIsLesson = next.some(activity => activity.type === 'videos' && /^(story|vocabulary)$/i.test(activity.label || ''));
    const own = acts(book, page).find(activity => activity.type === 'fill');
    const tracePage = own ? page : !nextIsLesson && next.some(activity => activity.type === 'fill') ? page + 1 : page;
    // the next page belongs to this lesson (its writing page and Formation video) unless it starts another one
    const pages = nextIsLesson || page === book.pages.length ? [page] : [page, page + 1];
    const all = pages.flatMap(p => acts(book, p));
    const game = all.find(activity => activity.type === 'game');
    const letters = /^[A-Za-z]{2}$/.test(name);
    lessons.push({
      letter: name, key: name, name, big: letters ? name[0] : name, small: letters ? name[1] : '', kind: config.kind, subject: config.subject,
      page, tracePage,
      words: (game?.targets || []).map(target => target.name), game,
      // the publisher's Story (or Vocabulary) video plays on the lesson page; the page's QR video otherwise
      lessonVideo: storyVideo(all) || lessonVideo(book, page),
      story: all.find(activity => activity.type === 'story'),
      videos: all.filter(activity => activity.type === 'videos'),
      trace: acts(book, tracePage).find(activity => activity.type === 'fill')
    });
  });
  return lessons;
}
