import turtle


t = turtle.Turtle()
t.pensize(1)
t.pencolor("purple")
  
def tree(n):
    if n < 10:
      return
    else:
      t.forward(n)
      t.left(30)
      tree(3 * n/4)
      t.left(60)
      tree(3 * n/4)
      t.left(30)
      t.backward(n)
    

tree(100)
turtle.exitonclick()