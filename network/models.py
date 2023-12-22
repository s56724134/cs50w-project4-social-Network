from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    content = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Post {self.id} made by {self.author}"
        
        
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")
    
    def __str__(self):
        return f"{self.user} is following {self.user_follower}"
    
        
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")
    
    def __str__(self):
        return f"{self.user} liked {self.post}"