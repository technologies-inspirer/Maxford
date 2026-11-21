import test from 'node:test';
import assert from 'node:assert/strict';
import { getSubjectAssignments, getLearningSubjects, getLearningBooks, learningBookMetadata, learningClasses, learningSubjects, libraryLink, schoolAllowsSelection } from '../src/data/learningCatalog.js';
import { series, seriesOf } from '../src/data/series.js';

globalThis.window = {};
await import('../books/library.js');
const books = window.PDF_BOOKS;

// A sample Maxford catalogue, so the library rules are checked before the real books arrive.
const sample = {
  'maxford-english-3': { classId: 'play-group', seriesId: 'maxford', subjectId: 'english' },
  'maxford-maths-3': { classId: 'play-group', seriesId: 'maxford', subjectId: 'maths' },
  'maxford-urdu-4': { classId: 'nursery', seriesId: 'maxford', subjectId: 'urdu' },
  'maxford-english-5': { classId: 'prep', seriesId: 'maxford', subjectId: 'english' },
  'maxford-old-draft': { classId: 'prep', seriesId: 'maxford', subjectId: 'maths' }
};
const sampleBooks = Object.keys(sample).map(id => ({ id }));
const hidden = new Set(['maxford-old-draft']);

test('Maxford Global has Play Group, Nursery and Prep only, youngest first, and one series', () => {
  assert.deepEqual(learningClasses.map(item => item.id), ['play-group', 'nursery', 'prep']);
  assert.deepEqual(series.map(item => item.id), ['maxford']);
  assert.equal(seriesOf({ id: 'any-new-book' }).id, 'maxford');
});

test('every book in the project has a valid class, subject and the Maxford series', () => {
  assert.deepEqual(Object.keys(learningBookMetadata).sort(), books.map(book => book.id).sort());
  for (const metadata of Object.values(learningBookMetadata)) {
    assert.ok(learningClasses.some(item => item.id === metadata.classId));
    assert.ok(learningSubjects.some(item => item.id === metadata.subjectId));
    assert.equal(metadata.seriesId, 'maxford');
  }
});

test('school selections filter class and subject choices without changing global assignments', () => {
  const account = { schoolAssignments: [{ classId: 'play-group', subjects: [{ seriesId: 'maxford', subjectId: 'maths' }] }] };
  assert.equal(schoolAllowsSelection(account, { classId: 'play-group' }), true);
  assert.equal(schoolAllowsSelection(account, { classId: 'nursery' }), false);
  assert.equal(schoolAllowsSelection(account, { classId: 'play-group', seriesId: 'maxford', subjectId: 'maths' }), true);
  assert.equal(schoolAllowsSelection(account, { classId: 'play-group', seriesId: 'maxford', subjectId: 'english' }), false);
  assert.equal(schoolAllowsSelection({}, { classId: 'prep' }), true);
  assert.equal(schoolAllowsSelection({ schoolAssignments: [] }, { classId: 'play-group' }), false);
  assert.equal(schoolAllowsSelection({ role: 'admin', schoolAssignments: [] }, { classId: 'play-group' }), true);
});

test('class, series and subject filters combine; hidden books stay out of the library', () => {
  const pick = selection => getLearningBooks(sampleBooks, selection, sample, hidden).map(book => book.id);
  assert.deepEqual(pick({ classId: 'play-group' }), ['maxford-english-3', 'maxford-maths-3']);
  assert.deepEqual(pick({ classId: 'play-group', seriesId: 'maxford', subjectId: 'english' }), ['maxford-english-3']);
  assert.deepEqual(pick({ classId: 'prep' }), ['maxford-english-5'], 'A hidden book is not listed');
  assert.deepEqual(getLearningBooks([], { classId: 'prep' }, sample, hidden), []);
  assert.deepEqual(getLearningBooks([{ id: 'not-in-catalogue' }], {}, sample, hidden), [], 'A book without a class is not listed');
  assert.deepEqual(getLearningBooks(sampleBooks), [], 'The real catalogue starts empty');
});

test('class options and selection links support the complete navigation flow', () => {
  assert.equal(libraryLink(), '#/user/library');
  assert.equal(libraryLink('play-group', 'maxford'), '#/user/library/play-group/maxford');
  assert.equal(libraryLink('nursery', 'maxford', 'urdu'), '#/user/library/nursery/maxford/urdu');
});

test('subjects come from the books of a class, and created subjects only from their own class', () => {
  const listed = sampleBooks.filter(book => !hidden.has(book.id));
  const subjects = (classId, custom = [], overrides = []) => getLearningSubjects(listed, custom, { classId, seriesId: 'maxford' }, overrides, sample).map(subject => subject.id);
  assert.deepEqual(subjects('play-group'), ['english', 'maths']);
  assert.deepEqual(subjects('nursery'), ['urdu']);
  const custom = [{ id: 'subject-test', name: 'Drawing', classId: 'prep', seriesId: 'maxford' }];
  assert.deepEqual(subjects('prep', custom), ['english', 'subject-test']);
  assert.ok(!subjects('play-group', custom).includes('subject-test'));
  assert.deepEqual(getLearningSubjects([], [], { classId: 'play-group', seriesId: 'maxford' }, [], sample), [], 'Subjects without their books stay hidden');
});

test('class assignments merge subject rows and update navigation without copying books', () => {
  const custom = [
    { id: 'subject-a', name: 'Drawing', classId: 'prep', seriesId: 'maxford' },
    { id: 'subject-b', name: 'Drawing', classId: 'nursery', seriesId: 'maxford' }
  ];
  const row = getSubjectAssignments(custom, [], sample).find(item => item.subjectId === 'subject-a');
  assert.deepEqual(row.classIds, ['prep', 'nursery']);
  const overrides = [{ seriesId: 'maxford', subjectId: 'maths', classIds: ['nursery'] }];
  const subjects = classId => getLearningSubjects(sampleBooks, custom, { classId, seriesId: 'maxford' }, overrides, sample).map(subject => subject.id);
  assert.ok(!subjects('play-group').includes('maths'), 'Unassigned from Play Group');
  assert.ok(subjects('nursery').includes('maths'), 'An admin assignment shows the subject in Nursery before its book arrives');
  assert.equal(getLearningBooks(sampleBooks, {}, sample, hidden).length, 4, 'Assignments never copy books');
});
