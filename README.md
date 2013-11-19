asteroids
=========

Simple Asteroids clone in Python, using pygame  

        _        _                 _     _
       / \   ___| |_ ___ _ __ ___ (_) __| |___
      / _ \ / __| __/ _ \ '__/ _ \| |/ _` / __|
     / ___ \\__ \ ||  __/ | | (_) | | (_| \__ \
    /_/   \_\___/\__\___|_|  \___/|_|\__,_|___/
    
    by Amin Bandali


## How To Play

To play the game, open a terminal (or command line window) and type:  
` python game.py `

Press Enter a click anywhere on the screen to start the game.  

You have 3 lives to begin with (displayed at top left).  
Each time a rock hits your spaceship, you lose a life.  
You have to avoid rocks.  

You begin with a 0 score (displayed at top right corner).  

You can move around:  
- use left and right (or "a" and "d" if you're a gamer) to rotate your spaceship
- use up arrow (or "w") to accelerate.

You can fire missiles using the "space bar".  
- When a missile hits a big rock, it breaks it into two medium sized ones. Your score goes up by 20.  
- When a missile hits a medium sized rock, it breaks it into two small ones. Your score goes up by 50.  
- When a missile hits a small rock, it destroys it completely and your score goes up by 100.  

The game gets more difficult for each 20 seconds you survive:  
- One more big rock is added to the screen (they were 4 initially)  
- The radius of rocks being created gets smaller, meaning that they will appear closer to your spaceship.  
