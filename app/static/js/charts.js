document.addEventListener('DOMContentLoaded', function () {
  const visitsCanvas = document.getElementById('visitsChart');
  const devicesCanvas = document.getElementById('devicesChart');

  function drawLineChart(canvas, data, color) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.clientWidth * window.devicePixelRatio;
    const h = canvas.height = canvas.clientHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

    const max = Math.max(...data);
    const min = Math.min(...data);
    const padding = 20;
    const innerW = canvas.clientWidth - padding * 2;
    const innerH = canvas.clientHeight - padding * 2;

    ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= 4; i++) {
      const y = padding + (innerH / 4) * i;
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.clientWidth - padding, y);
    }
    ctx.stroke();

    ctx.beginPath();
    data.forEach((value, index) => {
      const x = padding + (innerW / (data.length - 1)) * index;
      const y = canvas.clientHeight - padding - ((value - min) / (max - min || 1)) * innerH;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.stroke();

    const lastX = padding + (innerW / (data.length - 1)) * (data.length - 1);
    const lastY = canvas.clientHeight - padding - ((data[data.length - 1] - min) / (max - min || 1)) * innerH;
    ctx.beginPath();
    ctx.fillStyle = color;
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawDonutChart(canvas, labels, values, colors) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.clientWidth * window.devicePixelRatio;
    const h = canvas.height = canvas.clientHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

    const total = values.reduce((a, b) => a + b, 0);
    let start = -Math.PI / 2;
    const cx = canvas.clientWidth / 2;
    const cy = canvas.clientHeight / 2;
    const r = Math.min(canvas.clientWidth, canvas.clientHeight) * 0.28;

    values.forEach((value, index) => {
      const slice = (value / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, start, start + slice);
      ctx.closePath();
      ctx.fillStyle = colors[index];
      ctx.fill();
      start += slice;
    });

    ctx.beginPath();
    ctx.fillStyle = '#0b1220';
    ctx.arc(cx, cy, r * 0.54, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#e5eefb';
    ctx.font = '600 14px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Total', cx, cy - 4);
    ctx.font = '700 24px Inter, sans-serif';
    ctx.fillText(String(total), cx, cy + 24);
  }

  drawLineChart(visitsCanvas, [68, 76, 72, 82, 88, 94, 101, 110, 96, 108, 120, 118], '#6ee7b7');
  drawDonutChart(devicesCanvas, ['Mobile', 'Desktop', 'Tablet'], [58, 31, 11], ['#6ee7b7', '#7dd3fc', '#fbbf24']);

  window.addEventListener('resize', function () {
    drawLineChart(visitsCanvas, [68, 76, 72, 82, 88, 94, 101, 110, 96, 108, 120, 118], '#6ee7b7');
    drawDonutChart(devicesCanvas, ['Mobile', 'Desktop', 'Tablet'], [58, 31, 11], ['#6ee7b7', '#7dd3fc', '#fbbf24']);
  });
});
