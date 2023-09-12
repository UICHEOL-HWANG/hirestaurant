$(document).ready(function(){
    $('.like-form').on('submit',function(e){
        e.preventDefault()

        const form = $(this);
        const url = form.attr('action')
        const csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url : url,
            method : 'POST',
            headers : {
                'X-CSRFToken' : csrfToken,
            },

            success: function(data){
                // 서버로 받은 데이터로 좋아요 카운트 업데이트 

                const likeCount = form.find('.like-count');
                likeCount.text('좋아요 '+ data.like_count);

                const likeButton = form.find('.like-button');
                if(data.liked){
                    likeButton.html('<img width="21px" src="{% static "icons/ic-heart-filled.svg" %}" alt="filled like-icon">');
                }else{
                    likeButton.html('<img width="21px" src="{% static "icons/ic-heart.svg" %}" alt="like-icon">');
                }
            },
            error : function(error){
                console.log('Error',error);
            }
        })
    })
})