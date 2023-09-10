{
const menu = `
<div class="profile-menu">
    <a href="${profileURL}">내 프로필</a>
    <a href="${logoutURL}" class="warn"> 로그아웃</a>
</div>
`
tippy('.navbar .cp-avatar',{
content : menu,
placement : 'bottom-end',
arrow : false,
theme:'light',
trigger : 'click',
interactive : true,
allowHTML: true,
});
}