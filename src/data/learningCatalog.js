// UI classification only: original book IDs, page data and assets stay unchanged.
// Maxford Global has the early years only. The publisher's 3+ books are Play Group, 4+ Nursery and 5+ Prep.
export const learningClasses = [
  { id: 'play-group', name: 'Play Group' },
  { id: 'nursery', name: 'Nursery' },
  { id: 'prep', name: 'Prep' }
];

export const learningSubjects = [
  { id: 'english', name: 'English' },
  { id: 'urdu', name: 'Urdu' },
  { id: 'maths', name: 'Maths' },
  { id: 'computer', name: 'Computer' },
  { id: 'science', name: 'Science' },
  { id: 'social-studies', name: 'Social Studies' },
  { id: 'islamiat', name: 'Islamiat' }
];

// Where each book shows in the library. Add one line per book, for example:
//   'maxford-english-3': { classId: 'play-group', seriesId: 'maxford', subjectId: 'english' },
export const learningBookMetadata = {};

// Kept in the project but not shown in the reader's library. Remove an ID here to show that book again.
export const hiddenFromLibrary = new Set();

// Schools without explicit class selections retain their existing library access.
export function schoolAllowsSelection(account, selection) {
  if (account?.role === 'admin' || !Array.isArray(account?.schoolAssignments)) return true;
  return account.schoolAssignments.some(row => row.classId === selection.classId && (!selection.seriesId || row.subjects.some(subject => subject.seriesId === selection.seriesId && (!selection.subjectId || subject.subjectId === selection.subjectId))));
}

// `catalogue` and `hidden` default to the lists above; tests pass their own sample books.
export function getLearningBooks(books, selection = {}, catalogue = learningBookMetadata, hidden = hiddenFromLibrary) {
  return books.filter(book => {
    const metadata = catalogue[book.id];
    return metadata && !hidden.has(book.id) && ['classId', 'seriesId', 'subjectId'].every(key => !selection[key] || selection[key] === metadata[key]);
  });
}

export function getSubjectAssignments(customSubjects = [], overrides = [], catalogue = learningBookMetadata) {
  const rows = new Map();
  const add = (subject, seriesId, classId, hasBooks = false) => {
    const key = JSON.stringify([seriesId, subject.name.toLowerCase()]);
    if (!rows.has(key)) rows.set(key, { subjectId: subject.id, name: subject.name, seriesId, classIds: [], bookClassIds: [] });
    const row = rows.get(key);
    if (!row.classIds.includes(classId)) row.classIds.push(classId);
    if (hasBooks && !row.bookClassIds.includes(classId)) row.bookClassIds.push(classId);
  };
  Object.values(catalogue).forEach(meta => add(learningSubjects.find(s => s.id === meta.subjectId), meta.seriesId, meta.classId, true));
  customSubjects.forEach(subject => add(subject, subject.seriesId, subject.classId));
  return [...rows.values()].map(row => {
    const override = overrides.find(item => item.seriesId === row.seriesId && item.subjectId === row.subjectId);
    return { ...row, classIds: override ? override.classIds : row.classIds };
  });
}

export function getLearningSubjects(books, customSubjects, selection, assignments = [], catalogue = learningBookMetadata) {
  return getSubjectAssignments(customSubjects, assignments, catalogue)
    .filter(row => row.seriesId === selection.seriesId && row.classIds.includes(selection.classId))
    .filter(row => !row.bookClassIds.includes(selection.classId) || getLearningBooks(books, { ...selection, subjectId: row.subjectId }, catalogue).length > 0)
    .map(row => ({ id: row.subjectId, name: row.name }));
}

export function libraryLink(classId, seriesId, subjectId) {
  return '#/user/library' + [classId, seriesId, subjectId].filter(Boolean).map(part => `/${encodeURIComponent(part)}`).join('');
}
