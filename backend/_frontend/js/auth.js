{
const elts = document.querySelectorAll('[data-login-required]'); 
// createreview 를 가져온다 


function handleClick(e){
    if(!isAuthenticated){
        e.preventDefault();
        alert('로그인이 필요합니다.')
    }
}


// 로그인 요소가 필요한 부분들마다 반복적이게 넣어줌
for(let elt of elts){
elt.addEventListener('click',handleClick)
}

}