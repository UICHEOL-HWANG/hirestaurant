{
    const radioInputs = document.querySelectorAll('.rating input[type="radio"]')
    const starLabels = document.querySelectorAll('.rating label'); // 별 라벨 모두 가져오기 
    const cpStars = document.querySelector('.rating .cp-stars');

    let currentValue = initialRating; 

    

    function updateStars(value){
        for(let i=0; i<starLabels.length; i++){
            starLabels[i].classList.toggle('selected',i < value);
            // 선택된 값에 따라 selected 토글을 보여줌 
            // 만약 value 값보다 적으면 seleted 값이 사라짐 
            
        }
    }


    updateStars(currentValue);

    function handleChange(e){
        currentValue = e.target.value; 
        updateStars(currentValue)
    }



    // 마우스 별점 호버
    function handleEnter(e){ // 마우스에 갖다 대면 별점이 호버돼서 보이는 효과 
        const tempValue = e.target.querySelector('input').value; //레이블 안에 있는 input 선택 
        updateStars(tempValue); 
    }

    function handleLeave(e){ // 별점이 호버를 벗어나면 
        updateStars(currentValue);
    }

    for (let input of radioInputs){
        input.addEventListener('change',handleChange);
    }

    for(let star of starLabels){
        star.addEventListener('mouseenter',handleEnter);
    }

    cpStars.addEventListener('mouseleave',handleLeave); // 마우스가 마우스 rating을 넘어가면 해제  
}