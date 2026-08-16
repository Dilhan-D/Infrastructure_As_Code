document.addEventListener('DOMContentLoaded', function () {
  const burger = document.getElementById('burger');
  const navMobile = document.getElementById('navMobile');

  if (burger && navMobile) {
    burger.addEventListener('click', function () {
      navMobile.classList.toggle('is-open');
    });
  }
});
