# pylint: disable=too-many-locals
"""This module contains the functions needed to write the output to markdown files."""


from collections import defaultdict

from .contributor_stats import ContributorStats


def write_to_markdown(
    collaborators,
    filename,
    start_date,
    end_date,
    organization,
    repository,
    sponsor_info,
    link_to_profile,
    show_organizations_list,
):
    """
    This function writes a list of collaborators to a markdown file in table format.
    Each collaborator is represented as a dictionary with keys 'username', 'contribution_count', 'new_contributor', and 'commits'.

    Args:
        collaborators (list): A list of dictionaries, where each dictionary represents a collaborator.
                              Each dictionary should have the keys 'username', 'contribution_count', and 'commits'.
        filename (str): The path of the markdown file to which the table will be written.
        start_date (str): The start date of the date range for the contributor list.
        end_date (str): The end date of the date range for the contributor list.
        organization (str): The organization for which the contributors are being listed.
        repository (str): The repository for which the contributors are being listed.
        sponsor_info (str): True if the user wants the sponsor_url shown in the report
        link_to_profile (str): True if the user wants the username linked to Github profile in the report
        show_organizations_list (list): Organizations to show

    Returns:
        None

    """
    # Put together the contributor table
    table, total_contributions = get_contributor_table(
        collaborators,
        start_date,
        end_date,
        organization,
        repository,
        sponsor_info,
        link_to_profile,
        show_organizations_list,
    )

    # Put together the summary table including # of new contributions, # of new contributors, % new contributors, % returning contributors
    summary_table = get_summary_table(collaborators, start_date, end_date, total_contributions)

    # Write the markdown file
    write_markdown_file(filename, start_date, end_date, organization, repository, table, summary_table)


def write_markdown_file(filename, start_date, end_date, organization, repository, table, summary_table):
    """
    This function writes all the tables and data to a markdown file with tables to organizae the information.

    Args:
        filename (str): The path of the markdown file to which the table will be written.
        start_date (str): The start date of the date range for the contributor list.
        end_date (str): The end date of the date range for the contributor list.
        organization (str): The organization for which the contributors are being listed.
        repository (str): The repository for which the contributors are being listed.
        table (str): A string containing a markdown table of the contributors and the total contribution count.
        summary_table (str): A string containing a markdown table of the summary statistics.

    Returns:
        None

    """
    with open(filename, "w", encoding="utf-8") as markdown_file:
        markdown_file.write("# Contributors\n\n")
        if start_date and end_date:
            markdown_file.write(f"- Date range for contributor list:  {start_date} to {end_date}\n")
        if organization:
            markdown_file.write(f"- Organization: {organization}\n")
        if repository:
            markdown_file.write(f"- Repository: {repository}\n")
        markdown_file.write("\n")
        markdown_file.write(summary_table)
        if len(table) == 1 and "Independent" in table:
            markdown_file.write(table["Independent"])
        else:
            # Put independent last
            orgs = list(table.keys())
            if 'Independent' in orgs:
                orgs.remove('Independent')
                orgs.append('Independent')
            for org in orgs:
                org_title = f"## [{org}](https://github.com/{org})\n" if not org == "Independent" else f"## {org} \n"
                markdown_file.write(org_title)
                markdown_file.write(table[org])
        markdown_file.write(
            "\n _this file was generated by the [Organizational Contributors GitHub Action](https://github.com/HCookie/organizational_contributors)_\n"
        )


def get_summary_table(collaborators, start_date, end_date, total_contributions):
    """
    This function returns a string containing a markdown table of the summary statistics.

    Args:
        collaborators (list): A list of dictionaries, where each dictionary represents a collaborator.
                              Each dictionary should have the keys 'username', 'contribution_count', and 'commits'.
        start_date (str): The start date of the date range for the contributor list.
        end_date (str): The end date of the date range for the contributor list.
        total_contributions (int): The total number of contributions made by all of the contributors.

    Returns:
        summary_table (str): A string containing a markdown table of the summary statistics.

    """
    if start_date and end_date:
        summary_table = "| Total Contributors | Total Contributions | % New Contributors |\n| --- | --- | --- |\n"
        if len(collaborators) > 0:
            new_contributors_percentage = round(
                (len([x for x in collaborators if x.new_contributor is True])) / len(collaborators) * 100,
                2,
            )
        else:
            new_contributors_percentage = 0
        summary_table += (
            "| "
            + str(len(collaborators))
            + " | "
            + str(total_contributions)
            + " | "
            + str(new_contributors_percentage)
            + "% |\n\n"
        )
    else:
        summary_table = "| Total Contributors | Total Contributions |\n| --- | --- |\n"
        summary_table += "| " + str(len(collaborators)) + " | " + str(total_contributions) + " |\n\n"

    return summary_table

def get_contributor_table(
    collaborators: list[ContributorStats],
    start_date,
    end_date,
    organization,
    repository,
    sponsor_info,
    link_to_profile,
    show_organizations_list,
):
    """
    This function returns a string containing a markdown table of the contributors and the total contribution count.

    Args:
        collaborators (list): A list of dictionaries, where each dictionary represents a collaborator.
                              Each dictionary should have the keys 'username', 'contribution_count', and 'commits'.
        start_date (str): The start date of the date range for the contributor list.
        end_date (str): The end date of the date range for the contributor list.
        organization (str): The organization for which the contributors are being listed.
        repository (str): The repository for which the contributors are being listed.
        sponsor_info (str): True if the user wants the sponsor_url shown in the report
        link_to_profile (str): True if the user wants the username linked to Github profile in the report

    Returns:
        table (str): A string containing a markdown table of the contributors and the total contribution count.
        total_contributions (int): The total number of contributions made by all of the contributors.

    """
    columns = ["Username", "All Time Contribution Count"]
    if start_date and end_date:
        columns += ["New Contributor"]
    if sponsor_info == "true":
        columns += ["Sponsor URL"]
    if start_date and end_date:
        columns += [f"Commits between {start_date} and {end_date}"]
    else:
        columns += ["All Commits"]

    headers = "| " + " | ".join(columns) + " |\n"
    headers += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    total_contributions = 0

    organization_contributors = defaultdict(list)

    for collaborator in collaborators:
        total_contributions += collaborator.contribution_count
        username = collaborator.username
        contribution_count = collaborator.contribution_count
        if repository:
            commit_urls = collaborator.commit_url

        if not isinstance(repository, list):
            repository = [repository]

        if organization or len(repository) > 1:
            # split the urls from the comma separated list and make them into markdown links
            commit_url_list = collaborator.commit_url.split(",")
            commit_urls = ""
            for url in commit_url_list:
                url = url.strip()
                # get the organization and repository name from the url ie. org1/repo2 from https://github.com/org1/repo2/commits?author-zkoppert
                org_repo_link_name = url.split("/commits")[0].split("github.com/")[1]
                url = f"[{org_repo_link_name}]({url})"
                commit_urls += url + ", "
        new_contributor = collaborator.new_contributor

        row = f"| {'' if link_to_profile == 'false' else '@'}{username} | {contribution_count} |"
        if "New Contributor" in columns:
            row += f" {new_contributor} |"
        if "Sponsor URL" in columns:
            if collaborator.sponsor_info == "":
                row += " not sponsorable |"
            else:
                row += f" [Sponsor Link]({collaborator.sponsor_info}) |"
        row += f" {commit_urls} |\n"

        added_to_org: bool = False

        for org in collaborator.organizations or []:
            if org in show_organizations_list or "all" in show_organizations_list:
                organization_contributors[org].append(row)
                added_to_org = True
                break

        if not added_to_org:
            organization_contributors["Independent"].append(row)

    tables = {org: headers + "".join(rows) for org, rows in organization_contributors.items()}

    # table += row
    return tables, total_contributions
