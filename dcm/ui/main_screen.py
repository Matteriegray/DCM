from kivymd.uix.screen import MDScreen 
from kivymd.uix.boxlayout import MDBoxLayout 
from kivymd.uix.appbar import MDTopAppBar  
from kivymd.uix.tab import MDTabsCarousel , MDTabsItem 

class MainScreen(MDScreen): 
    """ Main application screen with navigation and content """ 
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.name = 'main_screen'  
                
        # Create the layout 
        layout = MDBoxLayout(orientation = 'vertical') 
        
        # Add toolbar 
        toolbar = MDTopAppBar(
            title = "DCM Playlist Generator" ,
            elevation = 10 ,
            left_action_items = [['menu', lambda x: print("menu clicked")]]  # TODO : add nav bar later  
        )
        layout.add_widget(toolbar) 
        
        # add layout to screen 
        self.add_widget(layout) 
 
        #Create tabs 
        tabs = MDTabsCarousel() 
        tabs.add_widget(MDTabsItem(text='Playlists', icon='playlist-music')) 
        tabs.add_widget(MDTabsItem(text='Library', icon='music')) 
        tabs.add_widget(MDTabsItem(text='Generate', icon='playlist-plus'))
        tabs.bind(on_index=self.on_tab_switch)  # Bind the tab switch event
        layout.add_widget(tabs)
    
    def on_tab_switch(self, instance, index):
        """Called when a tab is switched"""
        tab_text = instance.tab_bar.tab_list[index].text
        print(f"Switched to tab: {tab_text}")
        if tab_text == "Playlists":
            print("Loading playlists...")
        elif tab_text == "Library":
            print("Loading library...")
        elif tab_text == "Generate":
            print("Loading generator...")