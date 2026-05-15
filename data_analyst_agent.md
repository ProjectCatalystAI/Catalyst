================================================================================
Streaming Analyst
================================================================================

The following functions can be run by agents using MCP to retrieve information
about artists, tracks, and albums on various DSPs.

File structure:

* Spotify functions
    * get_popularity
        Return the popularity index. Useful to estimate the recent raising of
        popularity of an artist, track, or album.
    * search_spotify_id
        Auxiliary function for the previous one that searches for a query.

* Last.FM functions
    * get_lastfm_info
        Return various information such as playcount, listeners, genres, and
        similar artists.

* Soundcloud functions
    * get_soundcloud_info
        Return various information about tracks and users. Soundcloud has no
        native album type; they are treated as playlists.
    * search_soundcloud
        Auxiliary function for the previous one that searches for a query.
    * get_soundcloud_client_id
        We need to send a get request to the Soundcloud webpage in order to get
        the Client ID. This has to be done for every call to search_soundcloud,
        adding an overhead of a couple of seconds. Since these functions are
        called by an agent, it's not a big deal, and there are not other viable
        alternatives as far as I know.

TODO: YouTube functions.
TODO: If we want to monitor specific artists, tracks, or albums, we could let
      the agent execute these functions periodically (e.g., once a day) to save
      the relevant data into a CSV. It would help to understand how much an
      artist, track, or album is raising (e.g., monitoring the popularity
      index).
TODO: Functions that accept queries such as search_spotify_id and
      search_soundcloud return the first element of the search. While this will
      be correct most of the times, a more precise implementation should return
      a list of multiple elements (e.g., 5) among which the agent will choose
      the most relevant one.
TODO: At the end, we could cross-reference all the gathered data.