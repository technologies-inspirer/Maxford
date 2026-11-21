// Maxford Global publishes one series; every book belongs to it.
export const series = [
  { id: 'maxford', name: 'MaxFord Series', of: () => true }
];

export const seriesOf = book => series.find(item => item.of(book)) || series[0];
