$(document).ready(function () { 
    const navbar = $('.site-header.navbar');

    $(window).scroll(function () {
      // 현재 스크롤 위치를 가져옵니다.
      let scroll = $(window).scrollTop();
      
      // 스크롤 위치가 50 이하일 때 네비바의 클래스를 변경합니다.
      if (scroll <= 50) {
          $(".navbar").removeClass("scrolled");
      } 
      // 스크롤 위치가 50보다 큰 경우 네비바의 클래스를 변경합니다.
      else {
          $(".navbar").addClass("scrolled");
      }
    }); // 이 부분의 중괄호가 빠져있던 것 같습니다.
});